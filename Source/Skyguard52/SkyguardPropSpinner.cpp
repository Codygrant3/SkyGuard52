#include "SkyguardPropSpinner.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

ASkyguardPropSpinner::ASkyguardPropSpinner()
{
	PrimaryActorTick.bCanEverTick = true;

	Hub = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Hub"));
	SetRootComponent(Hub);
	Hub->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	BladeA = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BladeA"));
	BladeA->SetupAttachment(Hub);
	BladeA->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	BladeB = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BladeB"));
	BladeB->SetupAttachment(Hub);
	BladeB->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	BlurDisc = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BlurDisc"));
	BlurDisc->SetupAttachment(Hub);
	BlurDisc->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cyl(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Prop(TEXT("/Game/Skyguard/Meshes/Hero/propeller_proxy.propeller_proxy"));

	if (Cyl.Succeeded())
	{
		Hub->SetStaticMesh(Cyl.Object);
		Hub->SetRelativeScale3D(FVector(0.25f, 0.25f, 0.2f));
	}
	if (Prop.Succeeded())
	{
		BladeA->SetStaticMesh(Prop.Object);
		BladeB->SetStaticMesh(Prop.Object);
		BladeA->SetRelativeScale3D(FVector(0.55f, 0.55f, 0.55f));
		BladeB->SetRelativeScale3D(FVector(0.55f, 0.55f, 0.55f));
		BladeB->SetRelativeRotation(FRotator(0.f, 90.f, 0.f));
	}
	else if (Cube.Succeeded())
	{
		BladeA->SetStaticMesh(Cube.Object);
		BladeB->SetStaticMesh(Cube.Object);
		BladeA->SetRelativeScale3D(FVector(2.8f, 0.12f, 0.04f));
		BladeB->SetRelativeScale3D(FVector(2.8f, 0.12f, 0.04f));
		BladeB->SetRelativeRotation(FRotator(0.f, 90.f, 0.f));
	}
	if (Sphere.Succeeded())
	{
		BlurDisc->SetStaticMesh(Sphere.Object);
		BlurDisc->SetRelativeScale3D(FVector(2.4f, 2.4f, 0.05f));
	}
	if (UMaterialInterface* PropMat = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Skyguard/Materials/M_PropDisc.M_PropDisc")))
	{
		if (BlurDisc) BlurDisc->SetMaterial(0, PropMat);
		if (BladeA) BladeA->SetMaterial(0, PropMat);
		if (BladeB) BladeB->SetMaterial(0, PropMat);
	}
	if (UMaterialInterface* Metal = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Skyguard/Materials/M_Tex_airframe_metal.M_Tex_airframe_metal")))
	{
		if (Hub) Hub->SetMaterial(0, Metal);
	}
}

void ASkyguardPropSpinner::BeginPlay()
{
	Super::BeginPlay();
}

void ASkyguardPropSpinner::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	const float DegPerSec = SpinRPM * 6.f; // 360 deg * RPM / 60
	Angle = FMath::Fmod(Angle + DegPerSec * DeltaSeconds, 360.f);
	if (Hub)
	{
		Hub->SetRelativeRotation(FRotator(Angle, 0.f, 90.f));
	}
}
