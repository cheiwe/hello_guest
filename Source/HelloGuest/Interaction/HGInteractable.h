#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "HGInteractable.generated.h"

class AHGPlayerCharacter;

UINTERFACE(MinimalAPI, BlueprintType)
class UHGInteractable : public UInterface
{
	GENERATED_BODY()
};

class HELLOGUEST_API IHGInteractable
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "Hello Guest|Interaction")
	bool CanInteract(AHGPlayerCharacter* Player) const;

	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "Hello Guest|Interaction")
	void Interact(AHGPlayerCharacter* Player);

	/** Prompt under the crosshair: "Open", "Needs: Crowbar"... */
	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "Hello Guest|Interaction")
	FText GetInteractionText(AHGPlayerCharacter* Player) const;
};
