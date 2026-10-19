#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "HGDarkZone.generated.h"

class UBoxComponent;

/** Dark area (under a desk, a corner without light): the Guest only notices the player there up close. */
UCLASS()
class HELLOGUEST_API AHGDarkZone : public AActor
{
	GENERATED_BODY()

public:
	AHGDarkZone();

protected:
	virtual void BeginPlay() override;

	UFUNCTION()
	void HandleBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
		int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	UFUNCTION()
	void HandleEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UBoxComponent> Volume;
};
