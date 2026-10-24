#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "HGSafeZone.generated.h"

class UBoxComponent;

/**
 * Area the Guest never follows the player into (the player's side of the street). A chase ends at
 * its edge, noises and traces from inside are ignored.
 */
UCLASS()
class HELLOGUEST_API AHGSafeZone : public AActor
{
	GENERATED_BODY()

public:
	AHGSafeZone();

	/** True if the point lies inside any safe zone of the world. */
	static bool IsLocationSafe(const UObject* WorldContext, const FVector& Location);

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UBoxComponent> Volume;
};
