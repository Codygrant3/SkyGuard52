#pragma once

#include "CoreMinimal.h"
#include "SkyguardBossTypes.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardRadioChatterComponent.h"

class UObject;

/** Diegetic-enough pilot lines. No VO bank required for the first proof. */
namespace SkyguardPilotVoice
{
	FString ConfirmLineForCommand(ESkyguardPilotCommand Command);
	FString LineTextForEvent(ESkyguardPilotLine Line);
	float LineDurationForEvent(ESkyguardPilotLine Line);
	FSkyguardRadioLine MakeRadioLine(ESkyguardPilotLine Line);

	void ConfirmCommand(UObject* WorldContext, ESkyguardPilotCommand Command);
	void WarnOffAxis(UObject* WorldContext);
	void CallLock(UObject* WorldContext);
	void CallReload(UObject* WorldContext, const TCHAR* Station);
	void CallEvent(UObject* WorldContext, ESkyguardPilotLine Line);

	void ResetCallProbe();
	ESkyguardPilotLine GetLastCalledLine();
	FString GetLastCalledText();
	int32 GetCalledEventCount();
}
