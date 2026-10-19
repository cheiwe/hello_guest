#pragma once

#include "CoreMinimal.h"
#include "Interaction/HGInteractableBase.h"
#include "HGPickup.generated.h"

/** An item lying in the world. Sets the flag "Item.<ItemId>" when taken. */
UCLASS()
class HELLOGUEST_API AHGPickup : public AHGInteractableBase
{
	GENERATED_BODY()

public:
	AHGPickup();

	virtual void Interact_Implementation(AHGPlayerCharacter* Player) override;
	virtual FText GetInteractionText_Implementation(AHGPlayerCharacter* Player) const override;

protected:
	virtual void ApplyState() override;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Pickup")
	FName ItemId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Pickup")
	int32 Count = 1;

	UPROPERTY(SaveGame, BlueprintReadOnly, Category = "Pickup")
	bool bCollected = false;
};
