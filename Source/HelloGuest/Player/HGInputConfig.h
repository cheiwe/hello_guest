#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "HGInputConfig.generated.h"

class UInputAction;
class UInputMappingContext;

/**
 * Enhanced Input actions and the keyboard/gamepad mapping contexts, built in code so the
 * project is playable without any input assets. Can later be replaced by IA_/IMC_ assets.
 */
UCLASS()
class HELLOGUEST_API UHGInputConfig : public UObject
{
	GENERATED_BODY()

public:
	void Build();

	UPROPERTY() TObjectPtr<UInputAction> Move;
	UPROPERTY() TObjectPtr<UInputAction> LookMouse;
	UPROPERTY() TObjectPtr<UInputAction> LookGamepad;
	UPROPERTY() TObjectPtr<UInputAction> Jump;
	UPROPERTY() TObjectPtr<UInputAction> Crouch;
	UPROPERTY() TObjectPtr<UInputAction> Sprint;
	UPROPERTY() TObjectPtr<UInputAction> Interact;
	UPROPERTY() TObjectPtr<UInputAction> Use;
	UPROPERTY() TObjectPtr<UInputAction> NextItem;
	UPROPERTY() TObjectPtr<UInputAction> PreviousItem;
	UPROPERTY() TObjectPtr<UInputAction> Pause;

	UPROPERTY() TObjectPtr<UInputMappingContext> KeyboardContext;
	UPROPERTY() TObjectPtr<UInputMappingContext> GamepadContext;
};
