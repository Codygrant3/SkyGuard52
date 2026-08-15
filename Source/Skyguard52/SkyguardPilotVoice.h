#pragma once

#include "CoreMinimal.h"
#include "SkyguardBossTypes.h"
#include "SkyguardGunshipTypes.h"

class UObject;

/** Diegetic-enough pilot lines. No VO bank required for the first proof. */
namespace SkyguardPilotVoice
{
	void ConfirmCommand(UObject* WorldContext, ESkyguardPilotCommand Command);
	void WarnOffAxis(UObject* WorldContext);
	void CallLock(UObject* WorldContext);
	void CallReload(UObject* WorldContext, const TCHAR* Station);
	void CallEvent(UObject* WorldContext, ESkyguardPilotLine Line);
}
