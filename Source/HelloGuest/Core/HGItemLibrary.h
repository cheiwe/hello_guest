#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "HGItemLibrary.generated.h"

UCLASS()
class HELLOGUEST_API UHGItemLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** Localized item name shown in prompts and the inventory. */
	UFUNCTION(BlueprintPure, Category = "Hello Guest|Items")
	static FText GetItemDisplayName(FName ItemId);
};
