#include "SkyguardGunFireCameraShake.h"

USkyguardGunFireCameraShake::USkyguardGunFireCameraShake()
{
	bSingleInstance = false;
	OscillationDuration = 0.12f;
	OscillationBlendInTime = 0.02f;
	OscillationBlendOutTime = 0.08f;

	RotOscillation.Pitch.Amplitude = 0.4f;
	RotOscillation.Pitch.Frequency = 28.f;
	RotOscillation.Yaw.Amplitude = 0.18f;
	RotOscillation.Yaw.Frequency = 22.f;
	RotOscillation.Roll.Amplitude = 0.08f;
	RotOscillation.Roll.Frequency = 18.f;

	LocOscillation.X.Amplitude = 1.8f;
	LocOscillation.X.Frequency = 30.f;
	LocOscillation.Z.Amplitude = 0.6f;
	LocOscillation.Z.Frequency = 24.f;
}