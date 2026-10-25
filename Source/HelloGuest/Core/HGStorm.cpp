#include "Core/HGStorm.h"
#include "Components/AudioComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "TimerManager.h"

namespace
{
	/** Length of one flash pulse, seconds. */
	constexpr float PulseLength = 0.09f;
}

AHGStorm::AHGStorm()
{
	PrimaryActorTick.bCanEverTick = true;

	LightningLight = CreateDefaultSubobject<UDirectionalLightComponent>(TEXT("LightningLight"));
	LightningLight->SetIntensity(0.f);
	LightningLight->SetLightColor(FLinearColor(0.75f, 0.82f, 1.f));
	LightningLight->SetCastShadows(true);
	LightningLight->SetRelativeRotation(FRotator(-55.f, 35.f, 0.f));
	SetRootComponent(LightningLight);

	RainAudio = CreateDefaultSubobject<UAudioComponent>(TEXT("RainAudio"));
	RainAudio->SetupAttachment(LightningLight);
	RainAudio->bAllowSpatialization = false;
	RainAudio->bAutoActivate = true;
	RainAudio->SetVolumeMultiplier(0.55f);
}

void AHGStorm::BeginPlay()
{
	Super::BeginPlay();

	if (SkyDome)
	{
		SkyMaterial = SkyDome->GetStaticMeshComponent()->CreateAndSetMaterialInstanceDynamic(0);
		if (SkyMaterial)
		{
			SkyMaterial->SetScalarParameterValue(TEXT("EmissiveStrength"), SkyEmissive);
		}
	}
	ScheduleNext();
}

void AHGStorm::ScheduleNext()
{
	const float Delay = FMath::FRandRange(MinInterval, MaxInterval);
	GetWorldTimerManager().SetTimer(NextStrikeTimer, FTimerDelegate::CreateUObject(this, &AHGStorm::Strike, -1.f), Delay, false);
}

void AHGStorm::Strike(float Distance)
{
	StrikeDistance = Distance < 0.f ? FMath::FRand() : FMath::Clamp(Distance, 0.f, 1.f);
	StrikeStrength = FMath::Lerp(1.f, 0.35f, StrikeDistance);
	StrikeTime = GetWorld()->GetTimeSeconds();

	// Two to four flickers, the first one brightest, spaced unevenly like a real strike.
	Pulses.Reset();
	float Start = 0.f;
	const int32 Count = FMath::RandRange(2, 4);
	for (int32 Index = 0; Index < Count; ++Index)
	{
		Pulses.Add(FVector2f(Start, Index == 0 ? 1.f : FMath::FRandRange(0.4f, 0.9f)));
		Start += PulseLength + FMath::FRandRange(0.03f, 0.18f);
	}
	// Each strike comes from a slightly different direction.
	LightningLight->SetWorldRotation(FRotator(FMath::FRandRange(-70.f, -40.f), FMath::FRandRange(0.f, 360.f), 0.f));

	// Sound travels ~340 m/s: a close strike thunders almost at once, a far one seconds later.
	const float ThunderDelay = FMath::Lerp(0.15f, 3.5f, StrikeDistance);
	GetWorldTimerManager().SetTimer(ThunderTimer, this, &AHGStorm::PlayThunder, ThunderDelay, false);
	ScheduleNext();
}

void AHGStorm::PlayThunder()
{
	if (ThunderSounds.IsEmpty())
	{
		return;
	}
	const int32 Index = FMath::Clamp(FMath::RoundToInt(StrikeDistance * (ThunderSounds.Num() - 1)), 0, ThunderSounds.Num() - 1);
	if (USoundBase* Sound = ThunderSounds[Index])
	{
		UGameplayStatics::PlaySound2D(this, Sound, FMath::Lerp(1.f, 0.6f, StrikeDistance), FMath::FRandRange(0.9f, 1.05f));
	}
}

void AHGStorm::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	float Brightness = 0.f;
	if (StrikeTime >= 0.f)
	{
		const float Elapsed = GetWorld()->GetTimeSeconds() - StrikeTime;
		for (const FVector2f& Pulse : Pulses)
		{
			const float T = Elapsed - Pulse.X;
			if (T >= 0.f)
			{
				// Fast rise, quick fall, a short afterglow.
				const float Shape = T < PulseLength ? 1.f - T / PulseLength * 0.6f : 0.4f * FMath::Exp(-(T - PulseLength) * 9.f);
				Brightness = FMath::Max(Brightness, Shape * Pulse.Y);
			}
		}
		if (Elapsed > 2.f)
		{
			StrikeTime = -1.f;
		}
	}
	Brightness *= StrikeStrength;
	LightningLight->SetIntensity(FlashIntensity * Brightness);
	if (SkyMaterial)
	{
		SkyMaterial->SetScalarParameterValue(TEXT("EmissiveStrength"), FMath::Lerp(SkyEmissive, SkyFlashEmissive, Brightness));
	}
}
