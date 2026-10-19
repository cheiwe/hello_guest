#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameUserSettings.h"
#include "HGGameUserSettings.generated.h"

/**
 * Player options shared by all save slots: graphics (inherited), language, controls, audio, subtitles.
 * Stored in Saved/Config/<Platform>/GameUserSettings.ini.
 */
UCLASS()
class HELLOGUEST_API UHGGameUserSettings : public UGameUserSettings
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintPure, Category = "Hello Guest|Settings")
	static UHGGameUserSettings* GetHGGameUserSettings();

	virtual void SetToDefaults() override;

	/** Switches the game language immediately, without restarting. */
	UFUNCTION(BlueprintCallable, Category = "Hello Guest|Settings")
	void SetLanguage(const FString& InCulture);

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Settings")
	FString GetLanguage() const { return Culture; }

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Settings")
	TArray<FString> GetSupportedLanguages() const;

	/** Applies the stored language; on first launch picks the system language if it is supported. */
	void ApplyLanguage();

	UPROPERTY(Config, BlueprintReadWrite, Category = "Hello Guest|Settings")
	float MouseSensitivity = 1.f;

	UPROPERTY(Config, BlueprintReadWrite, Category = "Hello Guest|Settings")
	float GamepadSensitivity = 1.f;

	UPROPERTY(Config, BlueprintReadWrite, Category = "Hello Guest|Settings")
	bool bInvertLookY = false;

	UPROPERTY(Config, BlueprintReadWrite, Category = "Hello Guest|Settings")
	bool bGamepadVibration = true;

	UPROPERTY(Config, BlueprintReadWrite, Category = "Hello Guest|Settings")
	bool bSubtitles = true;

	/** 0 = small, 1 = medium, 2 = large. */
	UPROPERTY(Config, BlueprintReadWrite, Category = "Hello Guest|Settings")
	int32 SubtitleSize = 1;

	UPROPERTY(Config, BlueprintReadWrite, Category = "Hello Guest|Settings")
	float MasterVolume = 1.f;

	UPROPERTY(Config, BlueprintReadWrite, Category = "Hello Guest|Settings")
	float MusicVolume = 0.8f;

	UPROPERTY(Config, BlueprintReadWrite, Category = "Hello Guest|Settings")
	float EffectsVolume = 1.f;

private:
	/** Empty until the player (or first launch) picks a language. */
	UPROPERTY(Config)
	FString Culture;
};
