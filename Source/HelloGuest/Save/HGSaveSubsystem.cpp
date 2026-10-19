#include "Save/HGSaveSubsystem.h"
#include "Save/HGSaveable.h"
#include "Core/HGGameplaySettings.h"
#include "Core/HGWorldStateSubsystem.h"
#include "Player/HGPlayerCharacter.h"
#include "Player/HGInventoryComponent.h"
#include "AI/HGGuestCharacter.h"
#include "HelloGuest.h"
#include "EngineUtils.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameMapsSettings.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/PackageName.h"
#include "Serialization/MemoryReader.h"
#include "Serialization/MemoryWriter.h"
#include "Serialization/ObjectAndNameAsStringProxyArchive.h"
#include "TimerManager.h"
#include "UObject/UObjectGlobals.h"

namespace
{
	FString GetMapPackage(const UWorld* World)
	{
		return UWorld::RemovePIEPrefix(World->GetPackage()->GetName());
	}
}

UHGSaveSubsystem* UHGSaveSubsystem::Get(const UObject* WorldContextObject)
{
	const UGameInstance* GameInstance = UGameplayStatics::GetGameInstance(WorldContextObject);
	return GameInstance ? GameInstance->GetSubsystem<UHGSaveSubsystem>() : nullptr;
}

void UHGSaveSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);

	UHGWorldStateSubsystem* WorldState = Collection.InitializeDependency<UHGWorldStateSubsystem>();
	WorldState->OnFlagSet.AddDynamic(this, &UHGSaveSubsystem::HandleFlagSet);

	PostLoadMapHandle = FCoreUObjectDelegates::PostLoadMapWithWorld.AddUObject(this, &UHGSaveSubsystem::HandlePostLoadMap);
	SessionStartRealTime = FPlatformTime::Seconds();
}

void UHGSaveSubsystem::Deinitialize()
{
	FCoreUObjectDelegates::PostLoadMapWithWorld.Remove(PostLoadMapHandle);
	Super::Deinitialize();
}

FString UHGSaveSubsystem::MakeSlotName(int32 SlotIndex, bool bAutosave)
{
	return FString::Printf(TEXT("Slot%d_%s"), SlotIndex + 1, bAutosave ? TEXT("Auto") : TEXT("Manual"));
}

int32 UHGSaveSubsystem::GetSlotCount() const
{
	return FMath::Max(1, UHGGameplaySettings::Get()->SaveSlotCount);
}

float UHGSaveSubsystem::GetPlayTimeSeconds() const
{
	return PlayTimeAtSessionStart + static_cast<float>(FPlatformTime::Seconds() - SessionStartRealTime);
}

UWorld* UHGSaveSubsystem::GetGameWorld() const
{
	return GetGameInstance() ? GetGameInstance()->GetWorld() : nullptr;
}

void UHGSaveSubsystem::StartNewGame(int32 SlotIndex)
{
	CurrentSlot = FMath::Clamp(SlotIndex, 0, GetSlotCount() - 1);
	PendingLoad = nullptr;
	PlayTimeAtSessionStart = 0.f;
	SessionStartRealTime = FPlatformTime::Seconds();

	if (UHGWorldStateSubsystem* WorldState = GetGameInstance()->GetSubsystem<UHGWorldStateSubsystem>())
	{
		WorldState->ResetForNewGame();
	}

	const FString GameMap = FPackageName::ObjectPathToPackageName(UGameMapsSettings::GetGameDefaultMap());
	UGameplayStatics::OpenLevel(GetGameWorld(), FName(*GameMap));
}

bool UHGSaveSubsystem::CanSaveNow() const
{
	UWorld* World = GetGameWorld();
	if (!World)
	{
		return false;
	}

	const AHGPlayerCharacter* Player = Cast<AHGPlayerCharacter>(UGameplayStatics::GetPlayerCharacter(World, 0));
	if (!Player || Player->IsDead())
	{
		return false;
	}

	for (TActorIterator<AHGGuestCharacter> It(World); It; ++It)
	{
		if (It->IsChasing())
		{
			return false;
		}
	}
	return true;
}

bool UHGSaveSubsystem::ManualSave()
{
	return CanSaveNow() && SaveToSlot(CurrentSlot, false);
}

bool UHGSaveSubsystem::SaveToSlot(int32 SlotIndex, bool bAutosave)
{
	UWorld* World = GetGameWorld();
	UHGSaveGame* Save = World ? CaptureState(World, bAutosave) : nullptr;
	if (!Save)
	{
		return false;
	}

	const bool bSaved = UGameplayStatics::SaveGameToSlot(Save, MakeSlotName(SlotIndex, bAutosave), 0);
	if (bSaved)
	{
		UE_LOG(LogHelloGuest, Log, TEXT("Saved %s"), *MakeSlotName(SlotIndex, bAutosave));
		OnGameSaved.Broadcast(SlotIndex, bAutosave);
	}
	return bSaved;
}

UHGSaveGame* UHGSaveSubsystem::CaptureState(UWorld* World, bool bAutosave) const
{
	AHGPlayerCharacter* Player = Cast<AHGPlayerCharacter>(UGameplayStatics::GetPlayerCharacter(World, 0));
	const UHGWorldStateSubsystem* WorldState = GetGameInstance()->GetSubsystem<UHGWorldStateSubsystem>();
	if (!Player || !WorldState)
	{
		return nullptr;
	}

	UHGSaveGame* Save = Cast<UHGSaveGame>(UGameplayStatics::CreateSaveGameObject(UHGSaveGame::StaticClass()));
	Save->bAutosave = bAutosave;
	Save->Timestamp = FDateTime::Now();
	Save->PlayTimeSeconds = GetPlayTimeSeconds();
	Save->ProgressPercent = WorldState->GetProgressPercent();
	Save->MapPackage = GetMapPackage(World);
	Save->Flags = WorldState->GetFlags();
	Save->Values = WorldState->GetValues();
	Save->Inventory = Player->GetInventory()->GetEntries();
	Save->SelectedInventoryIndex = Player->GetInventory()->GetSelectedIndex();
	Save->PlayerTransform = Player->GetActorTransform();
	if (const AController* Controller = Player->GetController())
	{
		Save->ControlRotation = Controller->GetControlRotation();
	}

	for (TActorIterator<AActor> It(World); It; ++It)
	{
		AActor* Actor = *It;
		if (!Actor->Implements<UHGSaveable>())
		{
			continue;
		}

		FHGActorSaveRecord& Record = Save->Actors.AddDefaulted_GetRef();
		Record.ActorName = Actor->GetFName();

		FMemoryWriter Writer(Record.Data, true);
		FObjectAndNameAsStringProxyArchive Archive(Writer, true);
		Archive.ArIsSaveGame = true;
		Actor->Serialize(Archive);
	}

	return Save;
}

UHGSaveGame* UHGSaveSubsystem::LoadSaveObject(int32 SlotIndex, bool bAutosave) const
{
	const FString SlotName = MakeSlotName(SlotIndex, bAutosave);
	if (!UGameplayStatics::DoesSaveGameExist(SlotName, 0))
	{
		return nullptr;
	}

	UHGSaveGame* Save = Cast<UHGSaveGame>(UGameplayStatics::LoadGameFromSlot(SlotName, 0));
	if (Save && Save->Version != UHGSaveGame::LatestVersion)
	{
		Save->Migrate();
	}
	return Save;
}

UHGSaveGame* UHGSaveSubsystem::LoadNewest(int32 SlotIndex) const
{
	UHGSaveGame* Manual = LoadSaveObject(SlotIndex, false);
	UHGSaveGame* Auto = LoadSaveObject(SlotIndex, true);
	if (Manual && Auto)
	{
		return Manual->Timestamp >= Auto->Timestamp ? Manual : Auto;
	}
	return Manual ? Manual : Auto;
}

FHGSaveSlotInfo UHGSaveSubsystem::GetSlotInfo(int32 SlotIndex) const
{
	FHGSaveSlotInfo Info;
	Info.SlotIndex = SlotIndex;

	if (const UHGSaveGame* Save = LoadNewest(SlotIndex))
	{
		Info.bExists = true;
		Info.bAutosave = Save->bAutosave;
		Info.Timestamp = Save->Timestamp;
		Info.PlayTimeSeconds = Save->PlayTimeSeconds;
		Info.ProgressPercent = Save->ProgressPercent;
		Info.ThumbnailPng = Save->ThumbnailPng;
	}
	return Info;
}

void UHGSaveSubsystem::DeleteSlot(int32 SlotIndex)
{
	UGameplayStatics::DeleteGameInSlot(MakeSlotName(SlotIndex, false), 0);
	UGameplayStatics::DeleteGameInSlot(MakeSlotName(SlotIndex, true), 0);
}

bool UHGSaveSubsystem::LoadSlot(int32 SlotIndex)
{
	return BeginLoad(LoadNewest(SlotIndex), SlotIndex);
}

bool UHGSaveSubsystem::ContinueLastGame()
{
	int32 BestSlot = INDEX_NONE;
	FDateTime BestTime = FDateTime::MinValue();
	for (int32 Slot = 0; Slot < GetSlotCount(); ++Slot)
	{
		const FHGSaveSlotInfo Info = GetSlotInfo(Slot);
		if (Info.bExists && Info.Timestamp > BestTime)
		{
			BestTime = Info.Timestamp;
			BestSlot = Slot;
		}
	}
	return BestSlot != INDEX_NONE && LoadSlot(BestSlot);
}

bool UHGSaveSubsystem::BeginLoad(UHGSaveGame* Save, int32 SlotIndex)
{
	UWorld* World = GetGameWorld();
	if (!Save || !World)
	{
		return false;
	}

	CurrentSlot = SlotIndex;
	PlayTimeAtSessionStart = Save->PlayTimeSeconds;
	SessionStartRealTime = FPlatformTime::Seconds();

	if (GetMapPackage(World) == Save->MapPackage)
	{
		ApplyState(World, Save);
	}
	else
	{
		PendingLoad = Save;
		UGameplayStatics::OpenLevel(World, FName(*Save->MapPackage));
	}
	return true;
}

void UHGSaveSubsystem::HandlePostLoadMap(UWorld* World)
{
	if (PendingLoad && World && GetMapPackage(World) == PendingLoad->MapPackage)
	{
		UHGSaveGame* Save = PendingLoad;
		PendingLoad = nullptr;
		ApplyState(World, Save);
	}
}

void UHGSaveSubsystem::ApplyState(UWorld* World, UHGSaveGame* Save)
{
	if (UHGWorldStateSubsystem* WorldState = GetGameInstance()->GetSubsystem<UHGWorldStateSubsystem>())
	{
		WorldState->RestoreState(Save->Flags, Save->Values);
	}

	TMap<FName, AActor*> SaveableActors;
	for (TActorIterator<AActor> It(World); It; ++It)
	{
		if (It->Implements<UHGSaveable>())
		{
			SaveableActors.Add(It->GetFName(), *It);
		}
	}

	for (const FHGActorSaveRecord& Record : Save->Actors)
	{
		AActor* Actor = SaveableActors.FindRef(Record.ActorName);
		if (!Actor)
		{
			continue;
		}

		FMemoryReader Reader(Record.Data, true);
		FObjectAndNameAsStringProxyArchive Archive(Reader, true);
		Archive.ArIsSaveGame = true;
		Actor->Serialize(Archive);
		IHGSaveable::Execute_OnStateRestored(Actor);
	}

	if (AHGPlayerCharacter* Player = Cast<AHGPlayerCharacter>(UGameplayStatics::GetPlayerCharacter(World, 0)))
	{
		Player->GetInventory()->SetEntries(Save->Inventory, Save->SelectedInventoryIndex);
		Player->TeleportTo(Save->PlayerTransform.GetLocation(), Save->PlayerTransform.Rotator());
		if (AController* Controller = Player->GetController())
		{
			Controller->SetControlRotation(Save->ControlRotation);
		}
		Player->ResetAfterRespawn();
	}

	for (TActorIterator<AHGGuestCharacter> It(World); It; ++It)
	{
		It->ResetToHome();
	}
}

void UHGSaveSubsystem::HandleFlagSet(FName Flag)
{
	// Deferred so that the actor which set the flag finishes updating its own state first.
	if (UGameInstance* GameInstance = GetGameInstance())
	{
		GameInstance->GetTimerManager().SetTimer(AutosaveTimer, FTimerDelegate::CreateUObject(this, &UHGSaveSubsystem::TryAutosave), 0.2f, false);
	}
}

void UHGSaveSubsystem::TryAutosave()
{
	if (CanSaveNow())
	{
		SaveToSlot(CurrentSlot, true);
		return;
	}

	// Chase or death in progress: try again a bit later.
	GetGameInstance()->GetTimerManager().SetTimer(AutosaveTimer, FTimerDelegate::CreateUObject(this, &UHGSaveSubsystem::TryAutosave),
		UHGGameplaySettings::Get()->AutosaveRetryDelay, false);
}
