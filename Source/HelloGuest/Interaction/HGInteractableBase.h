#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Interaction/HGInteractable.h"
#include "Save/HGSaveable.h"
#include "HGInteractableBase.generated.h"

class UStaticMeshComponent;

/**
 * Base for everything the player can use. Optionally requires an item from the inventory
 * (crowbar, scissors, a key...) and sets a world-state flag when it is used.
 */
UCLASS(Abstract)
class HELLOGUEST_API AHGInteractableBase : public AActor, public IHGInteractable, public IHGSaveable
{
	GENERATED_BODY()

public:
	AHGInteractableBase();

	virtual bool CanInteract_Implementation(AHGPlayerCharacter* Player) const override;
	virtual void Interact_Implementation(AHGPlayerCharacter* Player) override;
	virtual FText GetInteractionText_Implementation(AHGPlayerCharacter* Player) const override;
	virtual void OnStateRestored_Implementation() override;

protected:
	virtual void BeginPlay() override;

	/** Refreshes visuals and collision from the saved state. */
	virtual void ApplyState() {}

	bool HasRequiredItem(const AHGPlayerCharacter* Player) const;
	FText GetMissingItemText() const;
	void SetWorldFlag(FName Flag) const;
	void EmitNoise(float Loudness, float Range);

	UFUNCTION(BlueprintImplementableEvent, Category = "Hello Guest|Interaction")
	void OnInteracted(AHGPlayerCharacter* Player);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USceneComponent> Root;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> Mesh;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Interaction")
	FText InteractionText;

	/** Item needed in the inventory; None means no requirement. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Interaction")
	FName RequiredItem;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Interaction")
	bool bConsumeRequiredItem = false;

	/** World-state flag set on a successful interaction (drives autosave and Guest phases). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Interaction")
	FName FlagOnUse;
};
