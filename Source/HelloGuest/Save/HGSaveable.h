#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "HGSaveable.generated.h"

UINTERFACE(MinimalAPI, BlueprintType)
class UHGSaveable : public UInterface
{
	GENERATED_BODY()
};

/**
 * Actors placed in the level whose UPROPERTY(SaveGame) fields are written to save slots
 * (opened locks, cleared obstacles, collected pickups...).
 */
class HELLOGUEST_API IHGSaveable
{
	GENERATED_BODY()

public:
	/** Called after the SaveGame properties were restored, to refresh visuals and collision. */
	UFUNCTION(BlueprintNativeEvent, Category = "Hello Guest|Save")
	void OnStateRestored();
};
