#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "HGThrowableProp.generated.h"

class UStaticMeshComponent;

/** Physics prop the player can carry and throw (inkwell, book, globe, bottles). Hard impacts make noise. */
UCLASS()
class HELLOGUEST_API AHGThrowableProp : public AActor
{
	GENERATED_BODY()

public:
	AHGThrowableProp();

protected:
	virtual void BeginPlay() override;

	UFUNCTION()
	void HandleHit(UPrimitiveComponent* HitComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, FVector NormalImpulse, const FHitResult& Hit);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> Mesh;

	/** Impacts faster than this make noise. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Noise")
	float NoiseSpeedThreshold = 350.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Noise")
	float NoiseLoudness = 0.7f;

private:
	double LastNoiseTime = -1.0;
};
