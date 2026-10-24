#include "Player/HGPlayerController.h"
#include "Player/HGInputConfig.h"
#include "Player/HGPlayerCharacter.h"
#include "Player/HGInventoryComponent.h"
#include "Core/HGGameUserSettings.h"
#include "Core/HGWorldStateSubsystem.h"
#include "Save/HGSaveSubsystem.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/LocalPlayer.h"
#include "Framework/Application/IInputProcessor.h"
#include "Framework/Application/SlateApplication.h"

#define LOCTEXT_NAMESPACE "HGPlayerController"

/** Watches raw Slate input to know whether the player is on keyboard/mouse or a gamepad. */
class FHGInputDeviceProcessor : public IInputProcessor
{
public:
	explicit FHGInputDeviceProcessor(TFunction<void(bool)> InCallback) : Callback(MoveTemp(InCallback)) {}

	virtual void Tick(const float DeltaTime, FSlateApplication& SlateApp, TSharedRef<ICursor> Cursor) override {}

	virtual bool HandleKeyDownEvent(FSlateApplication& SlateApp, const FKeyEvent& InKeyEvent) override
	{
		Callback(InKeyEvent.GetKey().IsGamepadKey());
		return false;
	}

	virtual bool HandleAnalogInputEvent(FSlateApplication& SlateApp, const FAnalogInputEvent& InAnalogInputEvent) override
	{
		if (InAnalogInputEvent.GetKey().IsGamepadKey() && FMath::Abs(InAnalogInputEvent.GetAnalogValue()) > 0.3f)
		{
			Callback(true);
		}
		return false;
	}

	virtual bool HandleMouseMoveEvent(FSlateApplication& SlateApp, const FPointerEvent& MouseEvent) override
	{
		if (MouseEvent.GetCursorDelta().SizeSquared() > 4.f)
		{
			Callback(false);
		}
		return false;
	}

	virtual bool HandleMouseButtonDownEvent(FSlateApplication& SlateApp, const FPointerEvent& MouseEvent) override
	{
		Callback(false);
		return false;
	}

private:
	TFunction<void(bool)> Callback;
};

UHGInputConfig* AHGPlayerController::GetInputConfig()
{
	if (!InputConfig)
	{
		InputConfig = NewObject<UHGInputConfig>(this);
		InputConfig->Build();
	}
	return InputConfig;
}

void AHGPlayerController::BeginPlay()
{
	Super::BeginPlay();

	if (!IsLocalController())
	{
		return;
	}

	if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(GetLocalPlayer()))
	{
		Subsystem->AddMappingContext(GetInputConfig()->KeyboardContext, 0);
		Subsystem->AddMappingContext(GetInputConfig()->GamepadContext, 0);
	}

	SetInputMode(FInputModeGameOnly());
	bShowMouseCursor = false;

	if (FSlateApplication::IsInitialized())
	{
		TWeakObjectPtr<AHGPlayerController> WeakThis(this);
		DeviceProcessor = MakeShared<FHGInputDeviceProcessor>([WeakThis](bool bGamepad)
		{
			if (WeakThis.IsValid())
			{
				WeakThis->SetUsingGamepad(bGamepad);
			}
		});
		FSlateApplication::Get().RegisterInputPreProcessor(DeviceProcessor);
	}
}

void AHGPlayerController::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (DeviceProcessor && FSlateApplication::IsInitialized())
	{
		FSlateApplication::Get().UnregisterInputPreProcessor(DeviceProcessor);
	}
	DeviceProcessor.Reset();

	Super::EndPlay(EndPlayReason);
}

void AHGPlayerController::SetUsingGamepad(bool bGamepad)
{
	if (bUsingGamepad != bGamepad)
	{
		bUsingGamepad = bGamepad;
		OnInputDeviceChanged.Broadcast(bUsingGamepad);
	}
}

FText AHGPlayerController::GetInteractKeyLabel() const
{
	return bUsingGamepad ? LOCTEXT("InteractGamepad", "X") : LOCTEXT("InteractKeyboard", "E");
}

void AHGPlayerController::TogglePauseMenu()
{
	// The pause menu widget is added in a later milestone; for now this only pauses the game.
	SetPause(!IsPaused());
}

void AHGPlayerController::HGSave()
{
	if (UHGSaveSubsystem* Saves = UHGSaveSubsystem::Get(this))
	{
		ClientMessage(Saves->ManualSave() ? TEXT("Saved") : TEXT("Cannot save now"));
	}
}

void AHGPlayerController::HGLoad(int32 Slot)
{
	if (UHGSaveSubsystem* Saves = UHGSaveSubsystem::Get(this))
	{
		ClientMessage(Saves->LoadSlot(Slot - 1) ? TEXT("Loaded") : TEXT("Slot is empty"));
	}
}

void AHGPlayerController::HGNewGame(int32 Slot)
{
	if (UHGSaveSubsystem* Saves = UHGSaveSubsystem::Get(this))
	{
		Saves->StartNewGame(Slot - 1);
	}
}

void AHGPlayerController::HGSlots()
{
	UHGSaveSubsystem* Saves = UHGSaveSubsystem::Get(this);
	if (!Saves)
	{
		return;
	}

	for (int32 Slot = 0; Slot < Saves->GetSlotCount(); ++Slot)
	{
		const FHGSaveSlotInfo Info = Saves->GetSlotInfo(Slot);
		ClientMessage(Info.bExists
			? FString::Printf(TEXT("Slot %d: %s, %.0f%%, %.0f min%s"), Slot + 1, *Info.Timestamp.ToString(), Info.ProgressPercent,
				Info.PlayTimeSeconds / 60.f, Info.bAutosave ? TEXT(" (auto)") : TEXT(""))
			: FString::Printf(TEXT("Slot %d: empty"), Slot + 1));
	}
}

void AHGPlayerController::HGLanguage(const FString& Culture)
{
	if (UHGGameUserSettings* Settings = UHGGameUserSettings::GetHGGameUserSettings())
	{
		Settings->SetLanguage(Culture);
	}
}

void AHGPlayerController::HGGive(FName ItemId)
{
	if (AHGPlayerCharacter* PlayerCharacter = Cast<AHGPlayerCharacter>(GetPawn()))
	{
		PlayerCharacter->GetInventory()->AddItem(ItemId);
	}
}

void AHGPlayerController::HGFlag(FName Flag)
{
	if (UHGWorldStateSubsystem* WorldState = UHGWorldStateSubsystem::Get(this))
	{
		WorldState->SetFlag(Flag);
	}
}

void AHGPlayerController::HGGod()
{
	if (AHGPlayerCharacter* PlayerCharacter = Cast<AHGPlayerCharacter>(GetPawn()))
	{
		PlayerCharacter->SetGodMode(!PlayerCharacter->IsGodMode());
		ClientMessage(PlayerCharacter->IsGodMode() ? TEXT("God mode ON") : TEXT("God mode OFF"));
	}
}

#undef LOCTEXT_NAMESPACE
