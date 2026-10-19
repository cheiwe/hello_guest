#include "Core/HGGameplaySettings.h"
#include "Animation/AnimSequence.h"
#include "Engine/SkeletalMesh.h"

void UHGGameplaySettings::SetGuestAssets(USkeletalMesh* Mesh, const TArray<USkeletalMesh*>& ExtraMeshes, UAnimSequence* Idle, UAnimSequence* Walk, UAnimSequence* Run,
	UAnimSequence* Search, UAnimSequence* Catch)
{
	UHGGameplaySettings* Settings = GetMutableDefault<UHGGameplaySettings>();
	Settings->GuestMesh = Mesh;
	Settings->GuestExtraMeshes.Reset();
	for (USkeletalMesh* Extra : ExtraMeshes)
	{
		if (Extra && Extra != Mesh)
		{
			Settings->GuestExtraMeshes.Add(Extra);
		}
	}
	Settings->GuestIdleAnim = Idle;
	Settings->GuestWalkAnim = Walk;
	Settings->GuestRunAnim = Run;
	Settings->GuestSearchAnim = Search;
	Settings->GuestCatchAnim = Catch;

#if WITH_EDITOR
	Settings->TryUpdateDefaultConfigFile();
#endif
}
