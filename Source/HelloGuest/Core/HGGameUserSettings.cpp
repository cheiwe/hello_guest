#include "Core/HGGameUserSettings.h"
#include "Core/HGGameplaySettings.h"
#include "Internationalization/Internationalization.h"
#include "Internationalization/Culture.h"
#include "Kismet/KismetInternationalizationLibrary.h"

UHGGameUserSettings* UHGGameUserSettings::GetHGGameUserSettings()
{
	return Cast<UHGGameUserSettings>(UGameUserSettings::GetGameUserSettings());
}

void UHGGameUserSettings::SetToDefaults()
{
	Super::SetToDefaults();

	MouseSensitivity = 1.f;
	GamepadSensitivity = 1.f;
	bInvertLookY = false;
	bGamepadVibration = true;
	bSubtitles = true;
	SubtitleSize = 1;
	MasterVolume = 1.f;
	MusicVolume = 0.8f;
	EffectsVolume = 1.f;
}

TArray<FString> UHGGameUserSettings::GetSupportedLanguages() const
{
	TArray<FString> Cultures = UHGGameplaySettings::Get()->SupportedCultures;
	if (Cultures.IsEmpty())
	{
		Cultures = { TEXT("en"), TEXT("ru") };
	}
	return Cultures;
}

void UHGGameUserSettings::SetLanguage(const FString& InCulture)
{
	if (!GetSupportedLanguages().Contains(InCulture))
	{
		return;
	}

	Culture = InCulture;
	ApplyLanguage();
	SaveSettings();
}

void UHGGameUserSettings::ApplyLanguage()
{
	const TArray<FString> Supported = GetSupportedLanguages();

	if (!Supported.Contains(Culture))
	{
		const FString SystemLanguage = FInternationalization::Get().GetCurrentLanguage()->GetTwoLetterISOLanguageName();
		Culture = Supported.Contains(SystemLanguage) ? SystemLanguage : Supported[0];
	}

	UKismetInternationalizationLibrary::SetCurrentCulture(Culture, false);
}
