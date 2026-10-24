#include "AI/HGGuestCharacter.h"
#include "AI/HGGuestAIController.h"
#include "Interaction/HGDoor.h"
#include "Core/HGGameplaySettings.h"
#include "Animation/AnimSequence.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "TimerManager.h"
#include "UObject/ConstructorHelpers.h"

AHGGuestCharacter::AHGGuestCharacter()
{
	// Ticks only once a real model is set up (animation switching).
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.bStartWithTickEnabled = false;

	// 2.3 m tall.
	GetCapsuleComponent()->InitCapsuleSize(40.f, 115.f);

	PlaceholderBody = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PlaceholderBody"));
	PlaceholderBody->SetupAttachment(GetCapsuleComponent());
	PlaceholderBody->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cylinder(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (Cylinder.Succeeded())
	{
		PlaceholderBody->SetStaticMesh(Cylinder.Object);
		PlaceholderBody->SetRelativeScale3D(FVector(0.7f, 0.7f, 2.3f));
	}

	AIControllerClass = AHGGuestAIController::StaticClass();
	AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;

	bUseControllerRotationYaw = false;
	UCharacterMovementComponent* Movement = GetCharacterMovement();
	Movement->bOrientRotationToMovement = true;
	Movement->RotationRate = FRotator(0.f, 360.f, 0.f);
	Movement->MaxWalkSpeed = UHGGameplaySettings::Get()->PatrolSpeed;
}

void AHGGuestCharacter::BeginPlay()
{
	Super::BeginPlay();
	HomeTransform = GetActorTransform();
	SetupModel();

	// The Guest is not stopped by doors: unlocked ones swing open, locked ones he simply passes.
	for (TActorIterator<AHGDoor> It(GetWorld()); It; ++It)
	{
		GetCapsuleComponent()->IgnoreActorWhenMoving(*It, true);
	}
}

bool AHGGuestCharacter::IsChasing() const
{
	const AHGGuestAIController* AI = Cast<AHGGuestAIController>(GetController());
	return AI && AI->IsChasing();
}

void AHGGuestCharacter::SetBaseSpeed(float Speed)
{
	BaseSpeed = Speed;
	GetCharacterMovement()->MaxWalkSpeed = BaseSpeed * SlowMultiplier;
}

void AHGGuestCharacter::SetIncapacitated(bool bValue)
{
	bIncapacitated = bValue;
	if (AHGGuestAIController* AI = Cast<AHGGuestAIController>(GetController()))
	{
		AI->SetIncapacitated(bValue);
	}
}

void AHGGuestCharacter::Stun(float Duration)
{
	SetIncapacitated(true);
	OnStunned(Duration);
	GetWorldTimerManager().SetTimer(StunTimer, this, &AHGGuestCharacter::EndStun, Duration, false);
}

void AHGGuestCharacter::EndStun()
{
	if (!GetWorldTimerManager().IsTimerActive(NeutralizeTimer))
	{
		SetIncapacitated(false);
	}
}

void AHGGuestCharacter::ApplySlow(float SpeedMultiplier, float Duration)
{
	SlowMultiplier = FMath::Clamp(SpeedMultiplier, 0.05f, 1.f);
	SetBaseSpeed(BaseSpeed);
	GetWorldTimerManager().SetTimer(SlowTimer, this, &AHGGuestCharacter::EndSlow, Duration, false);
}

void AHGGuestCharacter::EndSlow()
{
	SlowMultiplier = 1.f;
	SetBaseSpeed(BaseSpeed);
}

void AHGGuestCharacter::Neutralize()
{
	SetIncapacitated(true);
	SetActorHiddenInGame(true);
	SetActorEnableCollision(false);
	OnNeutralized(true);
	GetWorldTimerManager().SetTimer(NeutralizeTimer, this, &AHGGuestCharacter::EndNeutralize, UHGGameplaySettings::Get()->NeutralizeDuration, false);
}

void AHGGuestCharacter::EndNeutralize()
{
	SetActorHiddenInGame(false);
	SetActorEnableCollision(true);
	OnNeutralized(false);
	if (!GetWorldTimerManager().IsTimerActive(StunTimer))
	{
		SetIncapacitated(false);
	}
}

void AHGGuestCharacter::ResetToHome()
{
	GetWorldTimerManager().ClearTimer(StunTimer);
	GetWorldTimerManager().ClearTimer(SlowTimer);
	GetWorldTimerManager().ClearTimer(NeutralizeTimer);
	SlowMultiplier = 1.f;
	bPlayingCatch = false;
	OneShotUntil = 0.0;
	CurrentAnim = nullptr;
	SetActorHiddenInGame(false);
	SetActorEnableCollision(true);
	bIncapacitated = false;

	GetCharacterMovement()->StopMovementImmediately();
	TeleportTo(HomeTransform.GetLocation(), HomeTransform.Rotator());

	if (AHGGuestAIController* AI = Cast<AHGGuestAIController>(GetController()))
	{
		AI->ResetToPatrol();
	}
}

void AHGGuestCharacter::SetupModel()
{
	const UHGGameplaySettings* Settings = UHGGameplaySettings::Get();
	USkeletalMesh* SkeletalMesh = Settings->GuestMesh.LoadSynchronous();
	if (!SkeletalMesh)
	{
		return;
	}

	USkeletalMeshComponent* MeshComponent = GetMesh();
	MeshComponent->SetSkeletalMeshAsset(SkeletalMesh);
	MeshComponent->SetAnimationMode(EAnimationMode::AnimationSingleNode);

	// Fit the model to the capsule height and stand it on the capsule bottom.
	const float HalfHeight = GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
	const float ModelHeight = SkeletalMesh->GetImportedBounds().BoxExtent.Z * 2.f;
	const float Scale = ModelHeight > 1.f ? (HalfHeight * 2.f) / ModelHeight : 1.f;
	MeshComponent->SetRelativeScale3D(FVector(Scale));
	MeshComponent->SetRelativeLocation(FVector(0.f, 0.f, -HalfHeight));
	MeshComponent->SetRelativeRotation(FRotator(0.f, Settings->CharacterMeshYawOffset, 0.f));

	// Extra parts (the cloak) are separate meshes on the same skeleton: they copy the body's pose.
	for (const TSoftObjectPtr<USkeletalMesh>& ExtraPtr : Settings->GuestExtraMeshes)
	{
		if (USkeletalMesh* Extra = ExtraPtr.LoadSynchronous())
		{
			USkeletalMeshComponent* Part = NewObject<USkeletalMeshComponent>(this);
			Part->SetupAttachment(MeshComponent);
			Part->SetSkeletalMeshAsset(Extra);
			Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
			Part->RegisterComponent();
			Part->SetLeaderPoseComponent(MeshComponent);
		}
	}

	PlaceholderBody->SetVisibility(false);

	IdleAnim = Settings->GuestIdleAnim.LoadSynchronous();
	WalkAnim = Settings->GuestWalkAnim.LoadSynchronous();
	RunAnim = Settings->GuestRunAnim.LoadSynchronous();
	SearchAnim = Settings->GuestSearchAnim.LoadSynchronous();
	CatchAnim = Settings->GuestCatchAnim.LoadSynchronous();
	GiveUpAnim = Settings->GuestGiveUpAnim.LoadSynchronous();

	SetActorTickEnabled(true);
}

void AHGGuestCharacter::PlayLoop(UAnimSequence* Anim, float PlayRate)
{
	if (Anim && Anim != CurrentAnim)
	{
		GetMesh()->PlayAnimation(Anim, true);
		CurrentAnim = Anim;
	}
	GetMesh()->SetPlayRate(PlayRate);
}

void AHGGuestCharacter::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	if (bPlayingCatch || GetWorld()->GetTimeSeconds() < OneShotUntil)
	{
		return;
	}

	const float Speed = GetVelocity().Size2D();
	const UHGGameplaySettings* Settings = UHGGameplaySettings::Get();
	const AHGGuestAIController* AI = Cast<AHGGuestAIController>(GetController());

	if (!bIncapacitated && Speed > 10.f)
	{
		if (Speed > Settings->PatrolSpeed * 1.15f && RunAnim)
		{
			PlayLoop(RunAnim, 1.f);
		}
		else if (WalkAnim)
		{
			PlayLoop(WalkAnim, 1.f);
		}
		else
		{
			PlayLoop(RunAnim, 0.6f);
		}
	}
	else if (AI && AI->GetGuestState() == EHGGuestState::Search && SearchAnim)
	{
		PlayLoop(SearchAnim, 1.f);
	}
	else
	{
		PlayLoop(IdleAnim, 1.f);
	}
}

void AHGGuestCharacter::PlayCatchAnimation()
{
	if (CatchAnim)
	{
		bPlayingCatch = true;
		GetMesh()->PlayAnimation(CatchAnim, false);
		CurrentAnim = CatchAnim;
	}
}

float AHGGuestCharacter::PlayGiveUpAnimation(const FVector& LookAt)
{
	FVector ToTarget = LookAt - GetActorLocation();
	ToTarget.Z = 0.f;
	if (!ToTarget.IsNearlyZero())
	{
		SetActorRotation(ToTarget.Rotation());
	}

	if (!GiveUpAnim)
	{
		return 0.f;
	}

	GetMesh()->PlayAnimation(GiveUpAnim, false);
	GetMesh()->SetPlayRate(1.f);
	CurrentAnim = GiveUpAnim;
	const float Length = GiveUpAnim->GetPlayLength();
	OneShotUntil = GetWorld()->GetTimeSeconds() + Length;
	return Length;
}
