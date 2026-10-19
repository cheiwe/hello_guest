#include "Core/HGGameMode.h"
#include "Core/HGGameplaySettings.h"
#include "Core/HGGameUserSettings.h"
#include "Player/HGPlayerCharacter.h"
#include "Player/HGPlayerController.h"
#include "AI/HGGuestCharacter.h"
#include "UI/HGHUD.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerStart.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "TimerManager.h"

AHGGameMode::AHGGameMode()
{
	DefaultPawnClass = AHGPlayerCharacter::StaticClass();
	PlayerControllerClass = AHGPlayerController::StaticClass();
	HUDClass = AHGHUD::StaticClass();
}

void AHGGameMode::InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage)
{
	Super::InitGame(MapName, Options, ErrorMessage);

	if (UHGGameUserSettings* Settings = UHGGameUserSettings::GetHGGameUserSettings())
	{
		Settings->ApplyLanguage();
	}
}

void AHGGameMode::HandlePlayerCaught(AHGGuestCharacter* Guest, AHGPlayerCharacter* Player)
{
	if (!Guest || !Player || Player->IsDead())
	{
		return;
	}

	if (AController* Controller = Player->GetController())
	{
		const FVector GuestFace = Guest->GetActorLocation() + FVector(0.f, 0.f, Guest->BaseEyeHeight);
		Controller->SetControlRotation((GuestFace - Player->GetPawnViewLocation()).Rotation());
	}

	const TArray<TSoftObjectPtr<USoundBase>>& Screamers = UHGGameplaySettings::Get()->ScreamerSounds;
	if (!Screamers.IsEmpty())
	{
		if (USoundBase* Sound = Screamers[FMath::RandRange(0, Screamers.Num() - 1)].LoadSynchronous())
		{
			UGameplayStatics::PlaySound2D(this, Sound);
		}
	}

	OnScreamer(Guest, Player);
	Player->Die(EHGDeathReason::Caught);
}

void AHGGameMode::HandlePlayerDied(AHGPlayerCharacter* Player, EHGDeathReason Reason)
{
	const UHGGameplaySettings* Settings = UHGGameplaySettings::Get();
	const float Delay = Reason == EHGDeathReason::Caught ? Settings->CaughtRespawnDelay : Settings->FallRespawnDelay;

	TWeakObjectPtr<AHGPlayerCharacter> WeakPlayer(Player);
	FTimerHandle Handle;
	GetWorldTimerManager().SetTimer(Handle, FTimerDelegate::CreateWeakLambda(this, [this, WeakPlayer]()
	{
		if (WeakPlayer.IsValid())
		{
			RespawnPlayer(WeakPlayer.Get());
		}
	}), Delay, false);
}

void AHGGameMode::RespawnPlayer(AHGPlayerCharacter* Player)
{
	AController* Controller = Player->GetController();
	const AActor* Start = FindPlayerStart(Controller, UHGGameplaySettings::Get()->HomeSpawnTag.ToString());
	if (Start)
	{
		Player->TeleportTo(Start->GetActorLocation(), Start->GetActorRotation());
		if (Controller)
		{
			Controller->SetControlRotation(Start->GetActorRotation());
		}
	}

	Player->ResetAfterRespawn();

	for (TActorIterator<AHGGuestCharacter> It(GetWorld()); It; ++It)
	{
		It->ResetToHome();
	}

	Player->OnRespawned();
	OnPlayerRespawned(Player);
}
