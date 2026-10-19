#include "Player/HGPlayerCharacter.h"
#include "Player/HGInputConfig.h"
#include "Player/HGInventoryComponent.h"
#include "Player/HGPlayerController.h"
#include "Interaction/HGInteractable.h"
#include "Core/HGGameplaySettings.h"
#include "Core/HGGameUserSettings.h"
#include "Core/HGNoiseLibrary.h"
#include "Core/HGGameMode.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "EnhancedInputComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "InputActionValue.h"
#include "PhysicsEngine/PhysicsHandleComponent.h"
#include "TimerManager.h"

AHGPlayerCharacter::AHGPlayerCharacter()
{
	PrimaryActorTick.bCanEverTick = true;

	const UHGGameplaySettings* Settings = UHGGameplaySettings::Get();
	const float HalfHeight = Settings->PlayerHeight * 0.5f;

	GetCapsuleComponent()->InitCapsuleSize(34.f, HalfHeight);

	Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
	Camera->SetupAttachment(GetCapsuleComponent());
	Camera->SetRelativeLocation(FVector(0.f, 0.f, HalfHeight - 12.f));
	Camera->bUsePawnControlRotation = true;
	Camera->SetFieldOfView(90.f);

	Inventory = CreateDefaultSubobject<UHGInventoryComponent>(TEXT("Inventory"));
	PhysicsHandle = CreateDefaultSubobject<UPhysicsHandleComponent>(TEXT("PhysicsHandle"));

	UCharacterMovementComponent* Movement = GetCharacterMovement();
	Movement->GetNavAgentPropertiesRef().bCanCrouch = true;
	Movement->bCanWalkOffLedgesWhenCrouching = true;
	Movement->SetCrouchedHalfHeight(HalfHeight * 0.55f);
	Movement->MaxWalkSpeed = Settings->WalkSpeed;
	Movement->MaxWalkSpeedCrouched = Settings->CrouchSpeed;
	Movement->JumpZVelocity = 380.f;
	Movement->AirControl = 0.3f;

	bUseControllerRotationYaw = true;
}

void AHGPlayerCharacter::BeginPlay()
{
	Super::BeginPlay();
	UpdateMovementSpeed();
}

void AHGPlayerCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	AHGPlayerController* PC = Cast<AHGPlayerController>(GetController());
	UEnhancedInputComponent* Input = Cast<UEnhancedInputComponent>(PlayerInputComponent);
	if (!PC || !Input)
	{
		return;
	}

	const UHGInputConfig* Config = PC->GetInputConfig();
	Input->BindAction(Config->Move, ETriggerEvent::Triggered, this, &AHGPlayerCharacter::HandleMove);
	Input->BindAction(Config->LookMouse, ETriggerEvent::Triggered, this, &AHGPlayerCharacter::HandleLookMouse);
	Input->BindAction(Config->LookGamepad, ETriggerEvent::Triggered, this, &AHGPlayerCharacter::HandleLookGamepad);
	Input->BindAction(Config->Jump, ETriggerEvent::Started, this, &AHGPlayerCharacter::HandleJump);
	Input->BindAction(Config->Jump, ETriggerEvent::Completed, this, &AHGPlayerCharacter::HandleJumpStop);
	Input->BindAction(Config->Crouch, ETriggerEvent::Started, this, &AHGPlayerCharacter::HandleCrouch);
	Input->BindAction(Config->Sprint, ETriggerEvent::Started, this, &AHGPlayerCharacter::HandleSprintStart);
	Input->BindAction(Config->Sprint, ETriggerEvent::Completed, this, &AHGPlayerCharacter::HandleSprintStop);
	Input->BindAction(Config->Interact, ETriggerEvent::Started, this, &AHGPlayerCharacter::HandleInteract);
	Input->BindAction(Config->Use, ETriggerEvent::Started, this, &AHGPlayerCharacter::HandleUse);
	Input->BindAction(Config->NextItem, ETriggerEvent::Started, this, &AHGPlayerCharacter::HandleNextItem);
	Input->BindAction(Config->PreviousItem, ETriggerEvent::Started, this, &AHGPlayerCharacter::HandlePreviousItem);
	Input->BindAction(Config->Pause, ETriggerEvent::Started, this, &AHGPlayerCharacter::HandlePause);
}

void AHGPlayerCharacter::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	if (GetCharacterMovement()->IsFalling())
	{
		FallApexZ = FMath::Max(FallApexZ, GetActorLocation().Z);
	}

	UpdateFocus();
	UpdateHeldObject();
	UpdateFootstepNoise(DeltaSeconds);
}

// --- Input -------------------------------------------------------------------

void AHGPlayerCharacter::HandleMove(const FInputActionValue& Value)
{
	if (!CanAct())
	{
		return;
	}

	const FVector2D Axis = Value.Get<FVector2D>();
	const FRotator YawRotation(0.f, GetControlRotation().Yaw, 0.f);
	AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X), Axis.Y);
	AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y), Axis.X);
}

void AHGPlayerCharacter::HandleLookMouse(const FInputActionValue& Value)
{
	if (bInputLocked || bDead)
	{
		return;
	}

	const UHGGameUserSettings* UserSettings = UHGGameUserSettings::GetHGGameUserSettings();
	const float Sensitivity = UserSettings ? UserSettings->MouseSensitivity : 1.f;
	const float InvertY = (UserSettings && UserSettings->bInvertLookY) ? -1.f : 1.f;

	const FVector2D Axis = Value.Get<FVector2D>();
	AddControllerYawInput(Axis.X * Sensitivity);
	AddControllerPitchInput(Axis.Y * Sensitivity * InvertY);
}

void AHGPlayerCharacter::HandleLookGamepad(const FInputActionValue& Value)
{
	if (bInputLocked || bDead)
	{
		return;
	}

	const UHGGameUserSettings* UserSettings = UHGGameUserSettings::GetHGGameUserSettings();
	const float Sensitivity = UserSettings ? UserSettings->GamepadSensitivity : 1.f;
	const float InvertY = (UserSettings && UserSettings->bInvertLookY) ? -1.f : 1.f;
	const float Rate = UHGGameplaySettings::Get()->GamepadLookRate * Sensitivity * GetWorld()->GetDeltaSeconds();

	const FVector2D Axis = Value.Get<FVector2D>();
	AddControllerYawInput(Axis.X * Rate);
	AddControllerPitchInput(Axis.Y * Rate * InvertY);
}

void AHGPlayerCharacter::HandleJump()
{
	if (CanAct())
	{
		if (bIsCrouched)
		{
			UnCrouch();
		}
		Jump();
	}
}

void AHGPlayerCharacter::HandleJumpStop()
{
	StopJumping();
}

void AHGPlayerCharacter::HandleCrouch()
{
	if (!CanAct())
	{
		return;
	}

	if (bIsCrouched)
	{
		UnCrouch();
	}
	else
	{
		bSprinting = false;
		Crouch();
	}
	UpdateMovementSpeed();
}

void AHGPlayerCharacter::HandleSprintStart()
{
	if (bIsCrouched)
	{
		UnCrouch();
	}
	bSprinting = true;
	UpdateMovementSpeed();
}

void AHGPlayerCharacter::HandleSprintStop()
{
	bSprinting = false;
	UpdateMovementSpeed();
}

void AHGPlayerCharacter::HandleInteract()
{
	if (!CanAct())
	{
		return;
	}

	if (HeldComponent.IsValid())
	{
		ReleaseHeld(false);
		return;
	}

	AActor* Target = FocusedActor.Get();
	if (!Target)
	{
		return;
	}

	if (Target->Implements<UHGInteractable>())
	{
		if (IHGInteractable::Execute_CanInteract(Target, this))
		{
			IHGInteractable::Execute_Interact(Target, this);
		}
		return;
	}

	UPrimitiveComponent* Component = FocusedComponent.Get();
	if (Component && Component->IsSimulatingPhysics() && Component->GetMass() <= UHGGameplaySettings::Get()->MaxGrabMass)
	{
		PhysicsHandle->GrabComponentAtLocationWithRotation(Component, NAME_None, Component->GetComponentLocation(), Component->GetComponentRotation());
		HeldComponent = Component;
	}
}

void AHGPlayerCharacter::HandleUse()
{
	if (!CanAct())
	{
		return;
	}

	if (HeldComponent.IsValid())
	{
		ReleaseHeld(true);
		return;
	}

	const FName Selected = Inventory->GetSelectedItem();
	if (!Selected.IsNone())
	{
		OnUseSelectedItem(Selected);
	}
}

void AHGPlayerCharacter::HandleNextItem()
{
	Inventory->SelectNext();
}

void AHGPlayerCharacter::HandlePreviousItem()
{
	Inventory->SelectPrevious();
}

void AHGPlayerCharacter::HandlePause()
{
	if (AHGPlayerController* PC = Cast<AHGPlayerController>(GetController()))
	{
		PC->TogglePauseMenu();
	}
}

// --- Per-frame helpers ---------------------------------------------------------

void AHGPlayerCharacter::UpdateFocus()
{
	const FVector Start = Camera->GetComponentLocation();
	const FVector End = Start + Camera->GetForwardVector() * UHGGameplaySettings::Get()->InteractDistance;

	FCollisionQueryParams Params(SCENE_QUERY_STAT(HGInteractTrace), false, this);
	if (UPrimitiveComponent* Held = HeldComponent.Get())
	{
		Params.AddIgnoredComponent(Held);
	}

	FHitResult Hit;
	if (GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Params))
	{
		FocusedActor = Hit.GetActor();
		FocusedComponent = Hit.GetComponent();
	}
	else
	{
		FocusedActor.Reset();
		FocusedComponent.Reset();
	}
}

void AHGPlayerCharacter::UpdateHeldObject()
{
	if (!HeldComponent.IsValid())
	{
		return;
	}

	const FVector Target = Camera->GetComponentLocation() + Camera->GetForwardVector() * UHGGameplaySettings::Get()->HoldDistance;
	PhysicsHandle->SetTargetLocationAndRotation(Target, HeldComponent->GetComponentRotation());
}

void AHGPlayerCharacter::ReleaseHeld(bool bThrow)
{
	UPrimitiveComponent* Held = HeldComponent.Get();
	PhysicsHandle->ReleaseComponent();
	HeldComponent.Reset();

	if (Held && bThrow)
	{
		Held->AddImpulse(Camera->GetForwardVector() * UHGGameplaySettings::Get()->ThrowSpeed, NAME_None, true);
	}
}

void AHGPlayerCharacter::UpdateFootstepNoise(float DeltaSeconds)
{
	const UCharacterMovementComponent* Movement = GetCharacterMovement();
	const bool bMoving = Movement->IsMovingOnGround() && GetVelocity().Size2D() > 50.f;

	// Crouched movement is silent for the Guest.
	if (!bMoving || bIsCrouched)
	{
		FootstepTimer = 0.f;
		return;
	}

	FootstepTimer += DeltaSeconds;
	const UHGGameplaySettings* Settings = UHGGameplaySettings::Get();
	if (FootstepTimer >= Settings->FootstepNoiseInterval)
	{
		FootstepTimer = 0.f;
		const bool bRunning = bSprinting && GetVelocity().Size2D() > Settings->WalkSpeed + 20.f;
		ReportNoise(bRunning ? 0.8f : 0.3f, bRunning ? Settings->SprintNoiseRange : Settings->WalkNoiseRange);
	}
}

void AHGPlayerCharacter::UpdateMovementSpeed()
{
	const UHGGameplaySettings* Settings = UHGGameplaySettings::Get();
	GetCharacterMovement()->MaxWalkSpeed = bSprinting ? Settings->SprintSpeed : Settings->WalkSpeed;
	GetCharacterMovement()->MaxWalkSpeedCrouched = Settings->CrouchSpeed;
}

void AHGPlayerCharacter::ReportNoise(float Loudness, float Range)
{
	UHGNoiseLibrary::MakeNoiseAt(this, GetActorLocation(), Loudness, Range, this);
}

// --- Falling, stun, death --------------------------------------------------------

void AHGPlayerCharacter::OnMovementModeChanged(EMovementMode PrevMovementMode, uint8 PreviousCustomMode)
{
	Super::OnMovementModeChanged(PrevMovementMode, PreviousCustomMode);

	if (GetCharacterMovement()->MovementMode == MOVE_Falling)
	{
		FallApexZ = GetActorLocation().Z;
	}
}

void AHGPlayerCharacter::Landed(const FHitResult& Hit)
{
	Super::Landed(Hit);

	const UHGGameplaySettings* Settings = UHGGameplaySettings::Get();
	const float FallHeight = FallApexZ - GetActorLocation().Z;

	if (FallHeight >= Settings->PlayerHeight * Settings->DeathFallHeights)
	{
		ReportNoise(1.f, Settings->LandingNoiseRange);
		Die(EHGDeathReason::Fall);
	}
	else if (FallHeight >= Settings->PlayerHeight * Settings->StunFallHeights)
	{
		ReportNoise(1.f, Settings->LandingNoiseRange);
		Stun();
	}
	else if (FallHeight > 150.f && !bIsCrouched)
	{
		ReportNoise(0.5f, Settings->LandingNoiseRange * 0.5f);
	}
}

void AHGPlayerCharacter::Stun()
{
	bStunned = true;
	bSprinting = false;
	ReleaseHeld(false);
	GetCharacterMovement()->DisableMovement();
	OnStunned();

	GetWorldTimerManager().SetTimer(StunTimer, this, &AHGPlayerCharacter::EndStun, UHGGameplaySettings::Get()->StunDuration, false);
}

void AHGPlayerCharacter::EndStun()
{
	bStunned = false;
	if (!bDead)
	{
		GetCharacterMovement()->SetMovementMode(MOVE_Walking);
		UpdateMovementSpeed();
	}
}

void AHGPlayerCharacter::Die(EHGDeathReason Reason)
{
	if (bDead)
	{
		return;
	}

	bDead = true;
	bSprinting = false;
	ReleaseHeld(false);
	GetWorldTimerManager().ClearTimer(StunTimer);
	GetCharacterMovement()->DisableMovement();
	OnDied(Reason);

	if (AHGGameMode* GameMode = GetWorld()->GetAuthGameMode<AHGGameMode>())
	{
		GameMode->HandlePlayerDied(this, Reason);
	}
}

void AHGPlayerCharacter::ResetAfterRespawn()
{
	GetWorldTimerManager().ClearTimer(StunTimer);
	ReleaseHeld(false);
	bDead = false;
	bStunned = false;
	bSprinting = false;
	bInputLocked = false;
	DarkZoneCount = 0;
	UnCrouch();
	GetCharacterMovement()->StopMovementImmediately();
	GetCharacterMovement()->SetMovementMode(MOVE_Walking);
	UpdateMovementSpeed();
	FallApexZ = GetActorLocation().Z;
}
