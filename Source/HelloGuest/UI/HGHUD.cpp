#include "UI/HGHUD.h"
#include "Player/HGPlayerCharacter.h"
#include "Player/HGPlayerController.h"
#include "Player/HGInventoryComponent.h"
#include "Interaction/HGInteractable.h"
#include "Core/HGItemLibrary.h"
#include "Save/HGSaveSubsystem.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/Font.h"

#define LOCTEXT_NAMESPACE "HGHUD"

void AHGHUD::BeginPlay()
{
	Super::BeginPlay();

	if (UHGSaveSubsystem* Saves = UHGSaveSubsystem::Get(this))
	{
		Saves->OnGameSaved.AddDynamic(this, &AHGHUD::HandleGameSaved);
	}
}

void AHGHUD::HandleGameSaved(int32 SlotIndex, bool bAutosave)
{
	SaveIndicatorUntil = GetWorld()->GetRealTimeSeconds() + 2.0;
}

void AHGHUD::DrawLine(const FText& Text, float X, float Y, const FLinearColor& Color, float Scale)
{
	FCanvasTextItem Item(FVector2D(X, Y), Text, GEngine->GetMediumFont(), Color);
	Item.Scale = FVector2D(Scale);
	Item.EnableShadow(FLinearColor::Black);
	Canvas->DrawItem(Item);
}

void AHGHUD::DrawHUD()
{
	Super::DrawHUD();

	AHGPlayerController* PC = Cast<AHGPlayerController>(GetOwningPlayerController());
	AHGPlayerCharacter* Player = PC ? Cast<AHGPlayerCharacter>(PC->GetPawn()) : nullptr;
	if (!Canvas || !Player)
	{
		return;
	}

	const float CenterX = Canvas->ClipX * 0.5f;
	const float CenterY = Canvas->ClipY * 0.5f;

	// Crosshair dot.
	DrawRect(FLinearColor(1.f, 1.f, 1.f, 0.7f), CenterX - 2.f, CenterY - 2.f, 4.f, 4.f);

	// Interaction prompt.
	AActor* Focused = Player->GetFocusedActor();
	if (Focused && Focused->Implements<UHGInteractable>() && !Player->IsDead())
	{
		const FText Action = IHGInteractable::Execute_GetInteractionText(Focused, Player);
		if (!Action.IsEmpty())
		{
			const bool bCanUse = IHGInteractable::Execute_CanInteract(Focused, Player);
			const FText Prompt = bCanUse
				? FText::Format(LOCTEXT("Prompt", "[{0}] {1}"), PC->GetInteractKeyLabel(), Action)
				: Action;
			DrawLine(Prompt, CenterX + 20.f, CenterY + 20.f, bCanUse ? FLinearColor::White : FLinearColor(1.f, 0.6f, 0.5f));
		}
	}

	// Inventory, bottom left; the selected item is highlighted.
	const UHGInventoryComponent* Inventory = Player->GetInventory();
	const TArray<FHGInventoryEntry>& Entries = Inventory->GetEntries();
	float Y = Canvas->ClipY - 40.f - Entries.Num() * 22.f;
	for (int32 Index = 0; Index < Entries.Num(); ++Index)
	{
		const FText Name = UHGItemLibrary::GetItemDisplayName(Entries[Index].ItemId);
		const FText Line = Entries[Index].Count > 1
			? FText::Format(LOCTEXT("ItemCount", "{0} x{1}"), Name, Entries[Index].Count)
			: Name;
		const bool bSelected = Index == Inventory->GetSelectedIndex();
		DrawLine(Line, 30.f, Y, bSelected ? FLinearColor(1.f, 0.85f, 0.3f) : FLinearColor(0.85f, 0.85f, 0.85f));
		Y += 22.f;
	}

	if (GetWorld()->GetRealTimeSeconds() < SaveIndicatorUntil)
	{
		DrawLine(LOCTEXT("Saving", "Saving..."), Canvas->ClipX - 160.f, Canvas->ClipY - 50.f, FLinearColor::White);
	}

	if (Player->IsStunned())
	{
		DrawRect(FLinearColor(0.f, 0.f, 0.f, 0.35f), 0.f, 0.f, Canvas->ClipX, Canvas->ClipY);
	}
}

#undef LOCTEXT_NAMESPACE
