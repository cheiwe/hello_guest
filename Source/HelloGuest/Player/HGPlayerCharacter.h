#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Core/HGTypes.h"
#include "HGPlayerCharacter.generated.h"

class UCameraComponent;
class UHGInventoryComponent;
class UPhysicsHandleComponent;
struct FInputActionValue;

UCLASS()
class HELLOGUEST_API AHGPlayerCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	AHGPlayerCharacter();

	virtual void Tick(float DeltaSeconds) override;
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
	virtual void Landed(const FHitResult& Hit) override;

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Player")
	UHGInventoryComponent* GetInventory() const { return Inventory; }

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Player")
	UCameraComponent* GetCamera() const { return Camera; }

	/** Actor under the crosshair within interaction distance. */
	UFUNCTION(BlueprintPure, Category = "Hello Guest|Player")
	AActor* GetFocusedActor() const { return FocusedActor.Get(); }

	/** True while standing in a dark zone: the Guest only notices the player up close. */
	UFUNCTION(BlueprintPure, Category = "Hello Guest|Player")
	bool IsConcealed() const { return DarkZoneCount > 0; }

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Player")
	bool IsDead() const { return bDead; }

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Player")
	bool IsStunned() const { return bStunned; }

	bool IsHoldingObject() const { return HeldComponent.IsValid(); }

	void EnterDarkZone() { ++DarkZoneCount; }
	void ExitDarkZone() { DarkZoneCount = FMath::Max(0, DarkZoneCount - 1); }

	/** Kills the player; the game mode handles the screamer and the respawn. */
	void Die(EHGDeathReason Reason);

	/** Restores control after a respawn or a loaded save. Inventory is kept. */
	void ResetAfterRespawn();

	void SetInputLocked(bool bLocked) { bInputLocked = bLocked; }

	void ReportNoise(float Loudness, float Range);

	UFUNCTION(BlueprintImplementableEvent, Category = "Hello Guest|Player")
	void OnStunned();

	UFUNCTION(BlueprintImplementableEvent, Category = "Hello Guest|Player")
	void OnDied(EHGDeathReason Reason);

	/** Play the "sudden wake-up" animation here. */
	UFUNCTION(BlueprintImplementableEvent, Category = "Hello Guest|Player")
	void OnRespawned();

	/** The Use button with nothing held: space gun, placing items and similar. */
	UFUNCTION(BlueprintImplementableEvent, Category = "Hello Guest|Player")
	void OnUseSelectedItem(FName ItemId);

protected:
	virtual void BeginPlay() override;
	virtual void OnMovementModeChanged(EMovementMode PrevMovementMode, uint8 PreviousCustomMode) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UCameraComponent> Camera;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UHGInventoryComponent> Inventory;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UPhysicsHandleComponent> PhysicsHandle;

private:
	void HandleMove(const FInputActionValue& Value);
	void HandleLookMouse(const FInputActionValue& Value);
	void HandleLookGamepad(const FInputActionValue& Value);
	void HandleJump();
	void HandleJumpStop();
	void HandleCrouch();
	void HandleSprintStart();
	void HandleSprintStop();
	void HandleInteract();
	void HandleUse();
	void HandleNextItem();
	void HandlePreviousItem();
	void HandlePause();

	bool CanAct() const { return !bInputLocked && !bDead && !bStunned; }

	void UpdateFocus();
	void UpdateHeldObject();
	void UpdateFootstepNoise(float DeltaSeconds);
	void UpdateMovementSpeed();
	void ReleaseHeld(bool bThrow);
	void Stun();
	void EndStun();

	TWeakObjectPtr<AActor> FocusedActor;
	TWeakObjectPtr<UPrimitiveComponent> FocusedComponent;
	TWeakObjectPtr<UPrimitiveComponent> HeldComponent;

	float FallApexZ = 0.f;
	float FootstepTimer = 0.f;
	int32 DarkZoneCount = 0;
	bool bSprinting = false;
	bool bStunned = false;
	bool bDead = false;
	bool bInputLocked = false;

	FTimerHandle StunTimer;
};
