#include "UI/HGHUD.h"
#include "Player/HGPlayerCharacter.h"
#include "Player/HGPlayerController.h"
#include "Player/HGInventoryComponent.h"
#include "Interaction/HGInteractable.h"
#include "Core/HGItemLibrary.h"
#include "Save/HGSaveSubsystem.h"
#include "AI/HGGuestAIController.h"
#include "AI/HGGuestCharacter.h"
#include "CanvasItem.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/Font.h"
#include "Engine/World.h"
#include "EngineUtils.h"

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

void AHGHUD::DrawTextLine(const FText& Text, float X, float Y, const FLinearColor& Color, float Scale)
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
			DrawTextLine(Prompt, CenterX + 20.f, CenterY + 20.f, bCanUse ? FLinearColor::White : FLinearColor(1.f, 0.6f, 0.5f));
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
		DrawTextLine(Line, 30.f, Y, bSelected ? FLinearColor(1.f, 0.85f, 0.3f) : FLinearColor(0.85f, 0.85f, 0.85f));
		Y += 22.f;
	}

	DrawGuestAttention();

	if (Player->IsGodMode())
	{
		DrawTextLine(LOCTEXT("GodMode", "GOD MODE (G)"), 30.f, 30.f, FLinearColor(1.f, 0.85f, 0.3f));
	}

	if (GetWorld()->GetRealTimeSeconds() < SaveIndicatorUntil)
	{
		DrawTextLine(LOCTEXT("Saving", "Saving..."), Canvas->ClipX - 160.f, Canvas->ClipY - 50.f, FLinearColor::White);
	}

	if (Player->IsStunned())
	{
		DrawRect(FLinearColor(0.f, 0.f, 0.f, 0.35f), 0.f, 0.f, Canvas->ClipX, Canvas->ClipY);
	}
}

void AHGHUD::DrawGuestAttention()
{
	TActorIterator<AHGGuestCharacter> It(GetWorld());
	const AHGGuestAIController* AI = It ? Cast<AHGGuestAIController>(It->GetController()) : nullptr;
	if (!AI)
	{
		return;
	}

	const EHGGuestState State = AI->GetGuestState();
	const float Attention = State == EHGGuestState::Chase ? 1.f : FMath::Clamp(AI->GetAlert() / 100.f, 0.f, 1.f);

	FText Label;
	switch (State)
	{
	case EHGGuestState::Investigate: Label = LOCTEXT("GuestInvestigate", "Heard something"); break;
	case EHGGuestState::Search:      Label = LOCTEXT("GuestSearch", "Searching"); break;
	case EHGGuestState::Chase:       Label = LOCTEXT("GuestChase", "Chasing you!"); break;
	case EHGGuestState::GiveUp:      Label = LOCTEXT("GuestGiveUp", "Lost you"); break;
	case EHGGuestState::Incapacitated: Label = LOCTEXT("GuestStunned", "Stunned"); break;
	default:                         Label = LOCTEXT("GuestCalm", "Calm"); break;
	}

	// Green -> yellow -> red with attention; pulses while chasing.
	FLinearColor Color = Attention < 0.5f
		? FLinearColor::LerpUsingHSV(FLinearColor(0.2f, 0.8f, 0.3f), FLinearColor(1.f, 0.85f, 0.2f), Attention * 2.f)
		: FLinearColor::LerpUsingHSV(FLinearColor(1.f, 0.85f, 0.2f), FLinearColor(0.95f, 0.15f, 0.1f), (Attention - 0.5f) * 2.f);
	if (State == EHGGuestState::Chase)
	{
		Color.A = 0.6f + 0.4f * FMath::Abs(FMath::Sin(GetWorld()->GetRealTimeSeconds() * 6.f));
	}

	const float Width = 300.f;
	const float Height = 10.f;
	const float X = (Canvas->ClipX - Width) * 0.5f;
	const float Y = 36.f;
	DrawRect(FLinearColor(0.f, 0.f, 0.f, 0.5f), X - 2.f, Y - 2.f, Width + 4.f, Height + 4.f);
	DrawRect(Color, X, Y, Width * Attention, Height);
	DrawTextLine(Label, X, Y - 24.f, FLinearColor(0.9f, 0.9f, 0.9f), 0.9f);
}

#undef LOCTEXT_NAMESPACE
