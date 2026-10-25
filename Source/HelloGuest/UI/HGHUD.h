#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "HGHUD.generated.h"

/**
 * Minimal canvas HUD for the prototype: crosshair, interaction prompt, inventory, the Guest's
 * attention bar and the autosave indicator. The final UMG interface replaces it in a later milestone.
 */
UCLASS()
class HELLOGUEST_API AHGHUD : public AHUD
{
	GENERATED_BODY()

public:
	virtual void DrawHUD() override;

	/** Cutscene subtitle at the bottom of the screen; a new one replaces the current. */
	void ShowSubtitle(const FText& Text, float Duration);

protected:
	virtual void BeginPlay() override;

private:
	UFUNCTION()
	void HandleGameSaved(int32 SlotIndex, bool bAutosave);

	void DrawTextLine(const FText& Text, float X, float Y, const FLinearColor& Color, float Scale = 1.f);

	/** Bar at the top of the screen: how much attention the player has drawn from the Guest. */
	void DrawGuestAttention();

	void DrawSubtitle();

	double SaveIndicatorUntil = 0.0;
	FText SubtitleText;
	double SubtitleUntil = 0.0;
};
