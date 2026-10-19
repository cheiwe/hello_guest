#include "AI/HGGuestCharacter.h"
#include "AI/HGGuestAIController.h"
#include "Interaction/HGDoor.h"
#include "Core/HGGameplaySettings.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "TimerManager.h"
#include "UObject/ConstructorHelpers.h"

AHGGuestCharacter::AHGGuestCharacter()
{
	PrimaryActorTick.bCanEverTick = false;

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
