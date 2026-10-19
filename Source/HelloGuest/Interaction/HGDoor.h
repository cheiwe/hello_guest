#pragma once

#include "CoreMinimal.h"
#include "Interaction/HGInteractableBase.h"
#include "HGDoor.generated.h"

class AHGObstacle;
class UBoxComponent;

USTRUCT(BlueprintType)
struct FHGDoorLock
{
	GENERATED_BODY()

	// Every field is SaveGame: loading rebuilds the array, so unsaved fields would be lost.

	/** Sets the flag "Lock.<LockId>" when opened. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, SaveGame, Category = "Lock")
	FName LockId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, SaveGame, Category = "Lock")
	FName KeyItem;

	/** Locks of this door that must be opened first (the green lock needs all three chains). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, SaveGame, Category = "Lock")
	TArray<FName> RequiresLocks;

	/** An obstacle covering the lock (the spider web), must be cleared first. */
	UPROPERTY(EditInstanceOnly, BlueprintReadOnly, SaveGame, Category = "Lock")
	TObjectPtr<AHGObstacle> BlockedBy;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, SaveGame, Category = "Lock")
	bool bUnlocked = false;
};

/**
 * Hinged door with any number of locks. With no locks it is a plain door.
 * The Guest walks through doors (see AHGGuestCharacter) and swings unlocked ones open.
 */
UCLASS()
class HELLOGUEST_API AHGDoor : public AHGInteractableBase
{
	GENERATED_BODY()

public:
	AHGDoor();

	virtual void Tick(float DeltaSeconds) override;

	virtual bool CanInteract_Implementation(AHGPlayerCharacter* Player) const override;
	virtual void Interact_Implementation(AHGPlayerCharacter* Player) override;
	virtual FText GetInteractionText_Implementation(AHGPlayerCharacter* Player) const override;

	UFUNCTION(BlueprintPure, Category = "Door")
	bool IsFullyUnlocked() const;

	UFUNCTION(BlueprintCallable, Category = "Door")
	void SetOpen(bool bInOpen);

protected:
	virtual void BeginPlay() override;
	virtual void ApplyState() override;

	UFUNCTION(BlueprintImplementableEvent, Category = "Door")
	void OnLockOpened(FName LockId);

	UFUNCTION()
	void HandleGuestOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
		int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	/** Index of a lock the player can open right now, or INDEX_NONE. */
	int32 FindOpenableLock(const AHGPlayerCharacter* Player) const;
	bool IsLockReady(const FHGDoorLock& Lock) const;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USceneComponent> Hinge;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UBoxComponent> GuestDetector;

	UPROPERTY(EditAnywhere, SaveGame, BlueprintReadOnly, Category = "Door")
	TArray<FHGDoorLock> Locks;

	UPROPERTY(EditAnywhere, SaveGame, BlueprintReadOnly, Category = "Door")
	bool bOpen = false;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Door", meta = (Units = "deg"))
	float OpenAngle = 95.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Door", meta = (Units = "deg"))
	float SwingSpeed = 180.f;

private:
	float CurrentAngle = 0.f;
};
