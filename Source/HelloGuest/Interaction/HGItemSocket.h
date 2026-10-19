#pragma once

#include "CoreMinimal.h"
#include "Interaction/HGInteractableBase.h"
#include "HGItemSocket.generated.h"

/** A place where an item is installed: a lamp socket for a bulb, the fuse slot, the antenna mount on the spire. */
UCLASS()
class HELLOGUEST_API AHGItemSocket : public AHGInteractableBase
{
	GENERATED_BODY()

public:
	AHGItemSocket();

	virtual bool CanInteract_Implementation(AHGPlayerCharacter* Player) const override;
	virtual void Interact_Implementation(AHGPlayerCharacter* Player) override;
	virtual FText GetInteractionText_Implementation(AHGPlayerCharacter* Player) const override;

	UFUNCTION(BlueprintPure, Category = "Socket")
	bool IsFilled() const { return bFilled; }

protected:
	virtual void ApplyState() override;

	UFUNCTION(BlueprintImplementableEvent, Category = "Socket")
	void OnFilled(AHGPlayerCharacter* Player);

	/** Shown once the item is installed. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> InstalledMesh;

	UPROPERTY(SaveGame, BlueprintReadOnly, Category = "Socket")
	bool bFilled = false;
};
