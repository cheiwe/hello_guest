#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "HGStorm.generated.h"

class UAudioComponent;
class UDirectionalLightComponent;
class UMaterialInstanceDynamic;
class USoundBase;
class AStaticMeshActor;

/**
 * The night thunderstorm of Act 1: rain loop, lightning flashes at random intervals (a bright
 * directional light plus the sky dome flaring up, a few flickers per strike) and thunder that follows
 * the flash after a delay that grows with the distance of the strike.
 */
UCLASS()
class HELLOGUEST_API AHGStorm : public AActor
{
	GENERATED_BODY()

public:
	AHGStorm();

	virtual void Tick(float DeltaSeconds) override;

	/** Strikes now (also the console command HGLightning). Distance 0 = overhead, 1 = far away. */
	UFUNCTION(BlueprintCallable, Category = "Hello Guest|Storm")
	void Strike(float Distance = -1.f);

	/** Seconds between strikes. */
	UPROPERTY(EditAnywhere, Category = "Storm")
	float MinInterval = 7.f;

	UPROPERTY(EditAnywhere, Category = "Storm")
	float MaxInterval = 22.f;

	/** Peak intensity of the lightning light (lux) for a strike overhead. */
	UPROPERTY(EditAnywhere, Category = "Storm")
	float FlashIntensity = 8.f;

	/** Sky dome whose material's EmissiveStrength flares with the flashes. */
	UPROPERTY(EditAnywhere, Category = "Storm")
	TObjectPtr<AStaticMeshActor> SkyDome;

	UPROPERTY(EditAnywhere, Category = "Storm")
	float SkyEmissive = 1.f;

	UPROPERTY(EditAnywhere, Category = "Storm")
	float SkyFlashEmissive = 7.f;

	/** Thunder claps: index 0 is used for close strikes, the last for distant ones. */
	UPROPERTY(EditAnywhere, Category = "Storm")
	TArray<TObjectPtr<USoundBase>> ThunderSounds;

protected:
	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UDirectionalLightComponent> LightningLight;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UAudioComponent> RainAudio;

private:
	void ScheduleNext();
	void PlayThunder();

	UPROPERTY()
	TObjectPtr<UMaterialInstanceDynamic> SkyMaterial;

	/** Flicker pattern of the current strike: start times and strengths of the pulses. */
	TArray<FVector2f> Pulses;
	float StrikeTime = -1.f;
	float StrikeStrength = 0.f;
	float StrikeDistance = 0.f;
	FTimerHandle NextStrikeTimer;
	FTimerHandle ThunderTimer;
};
