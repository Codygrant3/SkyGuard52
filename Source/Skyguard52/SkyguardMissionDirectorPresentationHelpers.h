#pragma once

#include "CoreMinimal.h"

class UObject;
class USkyguardSortiePresentationComponent;

namespace SkyguardMissionDirectorPresentationHelpers
{
	SKYGUARD52_API void BindHudHostToPresentation(
		UObject* WorldContextObject,
		USkyguardSortiePresentationComponent* Presentation);
}
