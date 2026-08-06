#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "SkyguardMission01EnvironmentAuthoringLibrary.generated.h"

class ALandscape;
class ASkyguardMission01EnvironmentDirector;
class UPCGGraph;
class UMaterialInterface;
class USceneCaptureComponent2D;

UENUM(BlueprintType)
enum class ESkyguardLandscapeCaptureDiagnosticMode : uint8
{
	Lit,
	LandscapeCoverage,
	ShaderComplexity,
	ComponentBoundary
};

USTRUCT(BlueprintType)
struct FSkyguardLandscapeVisibleAudit
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bSuccess = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 LandscapeComponentCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 VisibleComponentCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 RegisteredComponentCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 RenderStateCreatedComponentCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 HiddenInGameComponentCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 GeneratedMaterialInstanceReadyComponentCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 GovernedMaterialParentMatchComponentCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 ContractCameraFrustumIntersectionCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bActorHiddenInGame = true;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bActorTemporarilyHiddenInEditor = true;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bBoundsFiniteAndNonzero = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FVector BoundsMinimum = FVector::ZeroVector;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FVector BoundsMaximum = FVector::ZeroVector;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FString Error;
};

USTRUCT(BlueprintType)
struct FSkyguardLandscapeCaptureConfigurationResult
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bSuccess = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	ESkyguardLandscapeCaptureDiagnosticMode Mode =
		ESkyguardLandscapeCaptureDiagnosticMode::Lit;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bUsesShowOnlyLandscape = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 ShowOnlyLandscapeComponentCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 GeneratedMaterialInstanceReadyComponentCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 DiagnosticMaterialParentMatchComponentCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bRenderThreadSynchronized = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FString CaptureSource;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FString ViewMode;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FString Error;
};

/** Native compilation/readiness audit for generated Landscape materials. */
USTRUCT(BlueprintType)
struct FSkyguardLandscapeMaterialCompilationResult
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bSuccess = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 LandscapeComponentCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 GeneratedMaterialInstanceCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 MaterialResourceCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 CompilationFinishedResourceCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 ValidShaderMapResourceCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bAssetCompilationQueueEmpty = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bShaderCompilationQueueEmpty = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FString Error;
};

USTRUCT(BlueprintType)
struct FSkyguardMission01EnvironmentAuthoringResult
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bSuccess = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	TObjectPtr<ALandscape> Landscape;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	TObjectPtr<UPCGGraph> Graph;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 LandscapeComponentCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FSkyguardLandscapeVisibleAudit VisibleAudit;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 GraphNodeCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 GraphEdgeCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	TArray<FString> GraphNodeSettingClasses;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bLandscapeGuidValid = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bLandscapeTransformExact = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bGraphContractValid = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bAuthoredStructureReady = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bLicensedMeshSlotsEmpty = true;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bGenerationLocked = true;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 GeneratedPCGComponentCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 GeneratedPCGInstanceCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bRouteAndBeachGeneratedInstancesZero = true;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FString Error;
};

/**
 * Editor-only deterministic authoring bridge for the governed M01 P4.4 pass.
 *
 * It creates one imported Landscape and one PCG graph in the current editor
 * world. It never saves packages and never invokes PCG generation. The Python
 * supervisor owns immutable path checks, persistence, receipts, and round-trip
 * validation.
 */
UCLASS()
class SKYGUARD52_API USkyguardMission01EnvironmentAuthoringLibrary
	: public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/**
	 * Returns the active render backend and maximum feature level as
	 * "<RHI>|<FeatureLevel>" (for example "D3D12|SM6"). The governed visible
	 * review harness uses this to fail before capture if a commandlet has
	 * silently selected NullRHI.
	 */
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Environment|Validation")
	static FString GetActiveRHIAndFeatureLevel();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Environment|Authoring")
	static FSkyguardMission01EnvironmentAuthoringResult
	AuthorGovernedLandscapeAndGraph(
		ASkyguardMission01EnvironmentDirector* Director,
		const FString& HeightmapSourcePath,
		const FString& GraphPackagePath);

	/**
	 * Imports the same governed Landscape into a new immutable world while
	 * binding the already accepted PCG graph. It never edits the graph and never
	 * invokes generation.
	 */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Environment|Authoring")
	static FSkyguardMission01EnvironmentAuthoringResult
	AuthorGovernedLandscapeWithExistingGraph(
		ASkyguardMission01EnvironmentDirector* Director,
		const FString& HeightmapSourcePath,
		const FString& GraphPackagePath);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Environment|Authoring")
	static FSkyguardMission01EnvironmentAuthoringResult
	AuditGovernedLandscapeAndGraph(
		ASkyguardMission01EnvironmentDirector* Director);

	/**
	 * Makes a newly imported governed Landscape explicitly render-ready and
	 * returns a live audit. This method never saves a package.
	 */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Environment|Validation")
	static FSkyguardLandscapeVisibleAudit
	PrepareGovernedLandscapeForVisibleValidation(
		ALandscape* Landscape,
		UMaterialInterface* GovernedMaterial);

	/** Read-only live render-readiness audit. */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Environment|Validation")
	static FSkyguardLandscapeVisibleAudit AuditLandscapeVisibleReadiness(
		ALandscape* Landscape,
		UMaterialInterface* GovernedMaterial);

	/**
	 * Blocks on UE asset/shader compilation, then finishes and audits the
	 * generated material resource for every governed Landscape component.
	 * UE 5.8 has no Landscape EMaterialUsage flag; readiness is therefore
	 * proven from the generated resources and their valid game-thread shader
	 * maps, never from unsupported Python property reflection.
	 */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Environment|Validation")
	static FSkyguardLandscapeMaterialCompilationResult
	FinishLandscapeMaterialCompilation(
		ALandscape* Landscape,
		UMaterialInterface* ExpectedParentMaterial);

	/** Read-only generated-resource audit; never waits, mutates, or saves. */
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Environment|Validation")
	static FSkyguardLandscapeMaterialCompilationResult
	AuditLandscapeMaterialCompilation(
		ALandscape* Landscape,
		UMaterialInterface* ExpectedParentMaterial);

	/**
	 * Starts an in-memory diagnostic-material transition, recreates the
	 * Landscape render state, and returns without blocking compilation
	 * managers. Recovery02 polls AuditLandscapeMaterialCompilation from later
	 * editor ticks and may capture only after two stable ready ticks.
	 */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Environment|Validation")
	static FSkyguardLandscapeVisibleAudit
	BeginTransientLandscapeDiagnosticMaterialDeferred(
		ALandscape* Landscape,
		UMaterialInterface* Material);

	/**
	 * Configures the SceneCapture view family directly. Editor viewport
	 * view-mode commands are deliberately not used.
	 */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Environment|Validation")
	static FSkyguardLandscapeCaptureConfigurationResult
	ConfigureLandscapeSceneCaptureDiagnostic(
		USceneCaptureComponent2D* Capture,
		ALandscape* Landscape,
		ESkyguardLandscapeCaptureDiagnosticMode Mode);

	/**
	 * Applies an in-memory-only Landscape material override and refreshes its
	 * generated component material instances. The capture harness must restore
	 * the governed material in a finally block; this method never saves.
	 */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Environment|Validation")
	static bool SetTransientLandscapeDiagnosticMaterial(
		ALandscape* Landscape,
		UMaterialInterface* Material);

	/**
	 * Applies an in-memory-only material, refreshes all generated Landscape
	 * instances, flushes the render thread, and returns the exact 16-component
	 * live audit. This method never saves a package.
	 */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Environment|Validation")
	static FSkyguardLandscapeVisibleAudit
	SetTransientLandscapeDiagnosticMaterialSynchronized(
		ALandscape* Landscape,
		UMaterialInterface* Material);
};
