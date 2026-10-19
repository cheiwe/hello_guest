#include "Player/HGInputConfig.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"

namespace
{
	UInputAction* MakeAction(UObject* Outer, const TCHAR* Name, EInputActionValueType ValueType)
	{
		UInputAction* Action = NewObject<UInputAction>(Outer, Name);
		Action->ValueType = ValueType;
		return Action;
	}

	template <typename TModifier>
	TModifier* AddModifier(FEnhancedActionKeyMapping& Mapping, UObject* Outer)
	{
		TModifier* Modifier = NewObject<TModifier>(Outer);
		Mapping.Modifiers.Add(Modifier);
		return Modifier;
	}
}

void UHGInputConfig::Build()
{
	Move = MakeAction(this, TEXT("IA_Move"), EInputActionValueType::Axis2D);
	LookMouse = MakeAction(this, TEXT("IA_LookMouse"), EInputActionValueType::Axis2D);
	LookGamepad = MakeAction(this, TEXT("IA_LookGamepad"), EInputActionValueType::Axis2D);
	Jump = MakeAction(this, TEXT("IA_Jump"), EInputActionValueType::Boolean);
	Crouch = MakeAction(this, TEXT("IA_Crouch"), EInputActionValueType::Boolean);
	Sprint = MakeAction(this, TEXT("IA_Sprint"), EInputActionValueType::Boolean);
	Interact = MakeAction(this, TEXT("IA_Interact"), EInputActionValueType::Boolean);
	Use = MakeAction(this, TEXT("IA_Use"), EInputActionValueType::Boolean);
	NextItem = MakeAction(this, TEXT("IA_NextItem"), EInputActionValueType::Boolean);
	PreviousItem = MakeAction(this, TEXT("IA_PreviousItem"), EInputActionValueType::Boolean);
	Pause = MakeAction(this, TEXT("IA_Pause"), EInputActionValueType::Boolean);
	Pause->bTriggerWhenPaused = true;

	// --- Keyboard and mouse ----------------------------------------------------
	KeyboardContext = NewObject<UInputMappingContext>(this, TEXT("IMC_Keyboard"));

	// WASD -> 2D axis: W/S drive Y (swizzled), A and S are negated.
	KeyboardContext->MapKey(Move, EKeys::D);
	AddModifier<UInputModifierNegate>(KeyboardContext->MapKey(Move, EKeys::A), this);
	AddModifier<UInputModifierSwizzleAxis>(KeyboardContext->MapKey(Move, EKeys::W), this);
	{
		FEnhancedActionKeyMapping& Back = KeyboardContext->MapKey(Move, EKeys::S);
		AddModifier<UInputModifierSwizzleAxis>(Back, this);
		AddModifier<UInputModifierNegate>(Back, this);
	}

	KeyboardContext->MapKey(LookMouse, EKeys::Mouse2D);
	KeyboardContext->MapKey(Jump, EKeys::SpaceBar);
	KeyboardContext->MapKey(Crouch, EKeys::LeftControl);
	KeyboardContext->MapKey(Crouch, EKeys::C);
	KeyboardContext->MapKey(Sprint, EKeys::LeftShift);
	KeyboardContext->MapKey(Interact, EKeys::E);
	KeyboardContext->MapKey(Use, EKeys::LeftMouseButton);
	KeyboardContext->MapKey(NextItem, EKeys::MouseScrollDown);
	KeyboardContext->MapKey(PreviousItem, EKeys::MouseScrollUp);
	KeyboardContext->MapKey(Pause, EKeys::Escape);
	KeyboardContext->MapKey(Pause, EKeys::P);

	// --- Gamepad ---------------------------------------------------------------
	GamepadContext = NewObject<UInputMappingContext>(this, TEXT("IMC_Gamepad"));

	AddModifier<UInputModifierDeadZone>(GamepadContext->MapKey(Move, EKeys::Gamepad_Left2D), this);
	AddModifier<UInputModifierDeadZone>(GamepadContext->MapKey(LookGamepad, EKeys::Gamepad_Right2D), this);
	GamepadContext->MapKey(Jump, EKeys::Gamepad_FaceButton_Bottom);
	GamepadContext->MapKey(Crouch, EKeys::Gamepad_FaceButton_Right);
	GamepadContext->MapKey(Sprint, EKeys::Gamepad_LeftThumbstick);
	GamepadContext->MapKey(Interact, EKeys::Gamepad_FaceButton_Left);
	GamepadContext->MapKey(Use, EKeys::Gamepad_RightTriggerAxis);
	GamepadContext->MapKey(NextItem, EKeys::Gamepad_RightShoulder);
	GamepadContext->MapKey(PreviousItem, EKeys::Gamepad_LeftShoulder);
	GamepadContext->MapKey(Pause, EKeys::Gamepad_Special_Right);
}
