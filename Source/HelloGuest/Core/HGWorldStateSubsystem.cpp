#include "Core/HGWorldStateSubsystem.h"
#include "Core/HGGameplaySettings.h"
#include "Engine/GameInstance.h"
#include "Kismet/GameplayStatics.h"

const FName UHGWorldStateSubsystem::SafeDigit3(TEXT("SafeDigit3"));
const FName UHGWorldStateSubsystem::SafeDigit4(TEXT("SafeDigit4"));

UHGWorldStateSubsystem* UHGWorldStateSubsystem::Get(const UObject* WorldContextObject)
{
	const UGameInstance* GameInstance = UGameplayStatics::GetGameInstance(WorldContextObject);
	return GameInstance ? GameInstance->GetSubsystem<UHGWorldStateSubsystem>() : nullptr;
}

void UHGWorldStateSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	ResetForNewGame();
}

void UHGWorldStateSubsystem::ResetForNewGame()
{
	Flags.Reset();
	Values.Reset();

	// The first two digits of the safe code are fixed ("5 3"), the last two change every playthrough.
	Values.Add(SafeDigit3, FMath::RandRange(0, 9));
	Values.Add(SafeDigit4, FMath::RandRange(0, 9));
}

void UHGWorldStateSubsystem::RestoreState(const TArray<FName>& InFlags, const TMap<FName, int32>& InValues)
{
	Flags = TSet<FName>(InFlags);
	Values = InValues;
}

void UHGWorldStateSubsystem::SetFlag(FName Flag)
{
	if (Flag.IsNone() || Flags.Contains(Flag))
	{
		return;
	}

	Flags.Add(Flag);
	OnFlagSet.Broadcast(Flag);
}

bool UHGWorldStateSubsystem::HasFlag(FName Flag) const
{
	return Flags.Contains(Flag);
}

void UHGWorldStateSubsystem::SetValue(FName Key, int32 Value)
{
	Values.Add(Key, Value);
}

int32 UHGWorldStateSubsystem::GetValue(FName Key, int32 DefaultValue) const
{
	const int32* Found = Values.Find(Key);
	return Found ? *Found : DefaultValue;
}

int32 UHGWorldStateSubsystem::GetGuestPhase() const
{
	int32 Phase = 0;
	for (const FHGGuestPhaseRule& Rule : UHGGameplaySettings::Get()->GuestPhaseRules)
	{
		if (Flags.Contains(Rule.Flag))
		{
			Phase = FMath::Max(Phase, Rule.Phase);
		}
	}
	return Phase;
}

float UHGWorldStateSubsystem::GetGuestSpeedMultiplier() const
{
	const int32 Phase = GetGuestPhase();
	for (const FHGGuestPhaseRule& Rule : UHGGameplaySettings::Get()->GuestPhaseRules)
	{
		if (Rule.Phase == Phase && Flags.Contains(Rule.Flag))
		{
			return Rule.SpeedMultiplier;
		}
	}
	return 1.f;
}

float UHGWorldStateSubsystem::GetProgressPercent() const
{
	const TArray<FName>& ProgressFlags = UHGGameplaySettings::Get()->ProgressFlags;
	if (ProgressFlags.IsEmpty())
	{
		return 0.f;
	}

	int32 Done = 0;
	for (const FName& Flag : ProgressFlags)
	{
		Done += Flags.Contains(Flag) ? 1 : 0;
	}
	return 100.f * Done / ProgressFlags.Num();
}
