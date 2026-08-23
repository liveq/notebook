# Dextop 코드 분석 — Galaxy Z Fold3 (SM-F926N / One UI 6.1) 포팅 가능성

- 대상 저장소: [NarYuki/Dextop](https://github.com/NarYuki/Dextop) `aa50d49` (Release 1.4.2)
- 구성: Flutter(UI) + Android 네이티브 Kotlin(전체 동작 로직), 네이티브 코드 약 14,700줄
- 분석 일자: 2026-08-23

---

## 0. 결론 요약

| 질문 | 답 |
| --- | --- |
| "One UI 8 이상" 제약이 코드에 있는가 | **없다.** `minSdk = 29`, Samsung 프로필은 `manufacturer == samsung`만 보고 SDK 하한이 없다. README/wiki의 문서상 제약일 뿐이다. |
| One UI 8에서 신설된 API에 의존하는가 | **앱이 호출하는 API 중 Android 16 전용 필수 항목은 없다.** 유일한 Android 16 API(`IDisplayManager.getDisplayTopology/setDisplayTopology`)는 실패해도 세션이 계속된다. |
| One UI 6.1(Android 14)에서 루팅 없이 동작하는가 | **삼성 덱스로는 불가.** 막히는 건 앱이 부르는 API가 아니라 **삼성 플랫폼 쪽 덱스 활성화 정책**이다. 앱을 아무리 고쳐도 One UI 6.1의 덱스는 가상/오버레이 디스플레이에 붙지 않는다. |
| 우회 여지 | **"삼성 덱스"는 포기하고 "AOSP 프리폼 데스크톱"으로 목표를 바꾸면 시도할 가치가 있다.** 코드에 이미 그 경로(`aospFreeform`)가 있고, 프로필 규칙 한 개 추가로 전환된다. 성공 확률은 중간 이하(§5). |

핵심 근거 한 줄: Dextop의 Samsung 프로필은 `platformManaged = true` / `startupMode = OEM_MANAGED` / `temporaryGlobalSettings = emptyMap()` 이다. 즉 **Dextop은 삼성 기기에서 데스크톱 모드를 강제하는 일을 전혀 하지 않는다.** 디스플레이를 하나 만들고 `CATEGORY_HOME`을 던진 뒤, 나머지는 전부 One UI가 알아서 덱스로 반응해 주기를 기다린다. One UI 8이 그렇게 반응하고 One UI 6.1/7은 그러지 않는다 — 이것이 제약의 실체다.

---

## 1. 요청한 5개 흐름의 파일·함수 단위 추적

### 1-1. 가상 디스플레이 생성 지점

**중요: `DisplayManager.createVirtualDisplay()` 공개 API를 쓰지 않는다.** 폰 세션의 디스플레이 생성은 **AOSP `OverlayDisplayAdapter`** 를 `Settings.Global` 쓰기로 간접 트리거하는 방식이다.

```
MainActivity.startDisplay()                       MainActivity.kt:648
  └─ MirrorService.launch(...)                    MirrorService.kt:178
      └─ MirrorService.start(config)              MirrorService.kt:1366
          ├─ addWindow()                          MirrorService.kt:1498   (호스트 SurfaceView 생성)
          └─ (SurfaceHolder 콜백) createDisplay()  MirrorService.kt:6309
              ├─ CapabilityProbe(...).run()       CapabilityProbe.kt:18
              ├─ desktopModeConfigurator.applyForCurrentDevice()
              │                                   DesktopModeConfigurator.kt:23
              ├─ clearOverlayDisplayRequestTwice() MirrorService.kt:4184
              └─ waitForOverlayRequestCleared()   MirrorService.kt:6438
                  └─ displayBackend.requestDisplay(w,h,density,secure,decorations)
                                                  DisplayMirrorBackend.kt:80
                      └─ Settings.Global.putString(
                             "overlay_display_devices",
                             "1920x1080/240,secure,should_show_system_decorations")
                                                  DisplayMirrorBackend.kt:106
                  └─ waitForOverlay(...)          MirrorService.kt:6496
                      └─ findCreatedDisplay()     DisplayMirrorBackend.kt:129
                         (Display.getType() == 4 == TYPE_OVERLAY 인 새 디스플레이 탐색, 100ms×40회)
```

- 설정 키 상수: `DisplayMirrorBackend.DISPLAY_SPECIFICATION = "overlay_display_devices"` (`DisplayMirrorBackend.kt:221`)
- 쓰기 권한: `WRITE_SECURE_SETTINGS` — Shizuku/Stellar 쉘로 `pm grant` (`MainActivity.grantSecureSettings()`, `MainActivity.kt:961`)
- 진짜 `createVirtualDisplay`는 **Android Auto(CARDEX) 경로에서만** 쓴다:
  `createDirectAutoDisplay()` `MirrorService.kt:6367` → `VirtualDisplayPlatform.openOwned()` `DisplayMirrorBackend.kt:349`
  → 리플렉션으로 `IDisplayManager.createVirtualDisplay(VirtualDisplayConfig, IVirtualDisplayCallback, ...)` 호출, flags = `PRESENTATION|OWN_CONTENT_ONLY|SUPPORTS_TOUCH|TRUSTED` (2|8|64|1024).

**생성 직후 디스플레이 설정** — `configureDisplay()` `MirrorService.kt:6687`, 전부 `IWindowManager` 히든 API:
| 호출 | 목적 |
| --- | --- |
| `setIgnoreOrientationRequest(id, true)` | 앱의 회전 요청 무시 |
| `setFixedToUserRotation(id, 2)` | 회전 고정 |
| `freezeDisplayRotation(id, rotation, ...)` | `applyDisplayRotation()` `:6730` |
| `setShouldShowSystemDecors(id, bool)` | **시스템 데코(태스크바/상태바) 표시 — 덱스 유발의 핵심 플래그** |
| `setDisplayImePolicy(id, 0)` | IME를 해당 디스플레이에 표시 |
| `clearForcedDisplaySize/DensityForUser` | `clearInheritedDisplayOverrides()` `:6668` |

### 1-2. Stellar / Shizuku 브리지 초기화 및 권한 위임

**Stellar는 별도 SDK가 없다. Shizuku API를 그대로 쓰고, 패키지명·바인더 재요청 브로드캐스트만 다르다.**

```
PrivilegedAccess.kt (전체 41줄) — 모든 권한 위임의 단일 통로
  ├─ isAvailable()  : Shizuku.getBinder()?.isBinderAlive          PrivilegedAccess.kt:11
  ├─ service(name, iface)                                          PrivilegedAccess.kt:15
  │    ShizukuBinderWrapper(SystemServiceHelper.getSystemService(name))
  │    → Class.forName("$iface\$Stub").asInterface(binder)
  │    (system_server의 IWindowManager/IDisplayManager/IInputManager를 shell 권한으로 호출)
  └─ execute(vararg args)                                          PrivilegedAccess.kt:23
       IShizukuService.newProcess(args, null, null)  ← 실제 쉘 프로세스 (settings/wm/cmd/uinput)
```

제공자 선택 및 초기화 (`MainActivity.kt`):
| 지점 | 내용 |
| --- | --- |
| `:29-30` | `STELLAR_PACKAGE = "roro.stellar.manager"`, `STELLAR_REQUEST_BINDER_ACTION = "roro.stellar.intent.action.REQUEST_BINDER"` |
| `selectedPrivilegeProvider()` `:576` | 둘 다 설치 시 사용자 선택 저장, 아니면 Stellar 우선 |
| `refreshBinderAvailability()` `:604` | `Shizuku.pingBinder()`; 죽어 있고 Stellar면 재요청 |
| `requestStellarBinder()` `:616` | `sendBroadcast(REQUEST_BINDER)`, `StellarBinderRetryGate`로 2s→30s 지수 백오프 |
| `binderReceivedListener` `:100` / `binderDeadListener` `:105` / `permissionListener` `:112` | Shizuku 공용 리스너 |
| `grantSecureSettings()` `:961` | 권한 승인 직후 `pm grant moe.n4tsu.dextop android.permission.WRITE_SECURE_SETTINGS` |
| Manifest `:10-11` | `moe.shizuku.manager.permission.API_V23`, `roro.stellar.manager.permission.API_V23` |

히든 API 블록리스트 우회: `HiddenApiBypass.addHiddenApiExemptions("")` — `MirrorService.onServiceConnected()` `:1177`, `DisplayTopologyController` `:336`. (`org.lsposed.hiddenapibypass:6.1`, `build.gradle.kts:113`)

### 1-3. 삼성 덱스 세션을 가상 디스플레이에 바인딩하는 지점

**명시적 바인딩 코드는 존재하지 않는다.** 저장소 전체에서 `com.samsung.*` 참조는 매니페스트의 `com.samsung.android.multidisplay.keep_process_alive` meta-data 단 하나뿐이고, `SemDesktopModeManager` 등 삼성 API 호출은 0건이다.

실제 "바인딩"은 다음 세 가지의 조합으로 **플랫폼이 자발적으로** 일으킨다:

1. `should_show_system_decorations` 플래그를 단 오버레이 디스플레이 생성 (`DisplayMirrorBackend.kt:88-92`)
2. `IWindowManager.setShouldShowSystemDecors(displayId, true)` (`MirrorService.kt:6720`)
3. `launchHome()` — `Intent(ACTION_MAIN).addCategory(CATEGORY_HOME)` + `ActivityOptions.setLaunchDisplayId(targetDisplayId)` (`MirrorService.kt:6760`)

→ One UI 8이 이 디스플레이의 HOME으로 덱스 셸(태스크바 포함)을 띄운다.

실패 시 복구 경로 (One UI가 HOME을 거부할 때):
```
launchHome() == false
  └─ retryHomeLaunchWithSystemDecorations()   MirrorService.kt:6818
       (decorations=true로 오버레이 재생성 → 1회만 재시도)
       └─ rememberSystemDecorationsForFirmware()  :6804  (Build.FINGERPRINT 단위로 기억)
```
`:6600` 주석 원문: *"One UI 8 rejects HOME launches on Samsung-owned virtual displays that do not advertise system decorations."*

덱스 세부 설정 조작은 `SamsungDesktopSettings.kt` — `settings put global external_display_resolution` 등 17개 키를 쉘로 write (`:105`), 최초 1회 백업(`:69`)/복원(`:84`).

### 1-4. 입력(터치/키/마우스) 주입 경로

세 갈래이고, 모두 최종적으로 shell 권한이 필요하다.

**(a) 이벤트 주입 — `InputDispatcher.kt` (39줄)**
```
InputDispatcher.send(event, displayId)               InputDispatcher.kt:20
  ├─ InputEvent.setDisplayId(displayId)   (히든)
  └─ IInputManager.injectInputEvent(event, 1 /*WAIT_FOR_RESULT*/)
```
호출부: `injectTouch()` `MirrorService.kt:6005`, `injectDirectTouch()` `:6041`(멀티터치/히스토리 좌표 스케일링), `injectKeyEvent()` `:5954`, `forwardKeyEvent()` `:5978`, `forwardMouseEvent()` `:5988`.

**(b) 커널 레벨 가상 포인터 — uinput**
```
startVirtualMouse()                                  MirrorService.kt:2018
  └─ IShizukuService.newProcess(arrayOf("uinput", "-"))
     → stdin으로 JSON 디바이스 기술자 전송
       profile "mouse":    EV_REL(REL_X/Y/WHEEL/HWHEEL) + BTN_LEFT/RIGHT/MIDDLE/SIDE/EXTRA
       profile "touchpad": 위 + EV_ABS(ABS_X/Y) + BTN_TOOL_FINGER/BTN_TOUCH
  ├─ virtualMouseMove/Button/Scroll()                :2248 / :2272 / :2283
  └─ 폴백: profile "software" (앱이 그린 커서 + 이벤트 주입)  updateVirtualCursorVisibility() :844
```

**(c) 물리 마우스 라우팅** — `startRawMouseReader()` `:7219`, `PhysicalDeviceRouting.kt`
(외부 디스플레이가 실제로 연결된 경우에만. 현재 삼성 기기에서는 대부분 비활성으로 처리)

입력 수신 측: `MirrorService`는 `AccessibilityService` (`:106`)로, 투명 오버레이 윈도우(`TouchRoutingFrame`, `addWindow()` `:1498`)에서 터치를 받아 위 경로로 재주입한다. 노트북 모드 키보드는 `handleLaptopKey()` `:3320` → `injectKey()` `:5936`.

### 1-5. 폴더블 힌지 각도 및 개폐 상태 감지

**두 개의 독립 소스를 쓰고, WindowManager 쪽을 우선한다.**

```
[소스 1] Jetpack WindowManager (androidx.window 1.5.1)
refreshFoldingApiState(reason)                        MirrorService.kt:2715
  └─ WindowInfoTracker.getOrCreate(activity).getCurrentWindowLayoutInfo(activity)
     → FoldingFeature.State.HALF_OPENED 여부 → foldingApiLaptopPosture
     → FoldingFeature.Orientation.HORIZONTAL 여부 → foldingApiHorizontalHinge
     (Activity 윈도우 토큰 필요 → MainActivity.currentActivity() 사용, 실패 시 유예시간 후 소스 2)

[소스 2] 힌지 각도 센서
onServiceConnected()                                  MirrorService.kt:1202
  └─ SensorManager.getDefaultSensor(Sensor.TYPE_HINGE_ANGLE)  → hingeListener 등록
updateLaptopModeForHinge(angle)                       MirrorService.kt:2427
  └─ 노이즈 필터: |Δ| ≥ 12° 면 스냅, 아니면 25% 저역통과 → filteredHingeAngle
  └─ isLaptopHingeAngle(angle)                        MirrorService.kt:2360
       비활성 시 55°~145° 진입 / 활성 시 45°~155° 유지 (히스테리시스)

[판정]
currentLaptopPosture()                                MirrorService.kt:2372
  └─ laptopFoldProfile()                              MirrorService.kt:2665
       FOLD8            → currentFold8LaptopPosture()  :2380  (API 우선, 기하학 폴백)
       STANDARD_FOLDABLE→ currentStandardFoldPosture() :2410  (API 우선, 센서 폴백)
       ※ Fold3는 모델 목록에 없으므로 else → STANDARD_FOLDABLE
  └─ evaluateLaptopModeForPosture()                   MirrorService.kt:2461
       └─ setLaptopMode(enabled)                      MirrorService.kt:1852
            └─ buildLaptopDeck() :1653 (US 키보드+트랙패드) / applyLaptopGeometryWhenLaidOut() :2538

[개폐에 따른 해상도 자동 전환]
displayListener (DisplayManager.DisplayListener)      MirrorService.kt:993
hostDisplayMonitor (주기 폴링)                          MirrorService.kt:~1150
  └─ shouldFollowHostDisplay()                        MirrorService.kt:6981
       (해상도 프로필이 "device" 이고 폴더블일 때만 true)
  └─ scheduleHostDisplayReconfiguration()             MirrorService.kt:7044  (320ms 디바운스)
       └─ configForHostGeometry()                     MirrorService.kt:7184  (밀도 자동 산출 160~320)
       └─ resizeActiveDisplay()                       MirrorService.kt:7096
            └─ IDisplayManager.resizeVirtualDisplay()  (태스크 유지한 채 논리 크기만 변경)
               ManagedVirtualDisplay.update()          DisplayMirrorBackend.kt:514

[기기 판정]
isFoldableDevice()      :2771  FoldingFeature 존재 || 내부 디스플레이 2개 이상 || TYPE_HINGE_ANGLE 센서 존재
isLaptopCapableDevice() :2791  폴더블이거나 smallestScreenWidthDp ≥ 600
```

### 1-6. (참고) 미러링 백엔드 — 가상 디스플레이 → 실제 화면

`DisplayMirrorBackend.attach()` `DisplayMirrorBackend.kt:135`가 전략을 순서대로 시도한다.

| id | 구현 | 위치 |
| --- | --- | --- |
| `virtual_display` | `IDisplayManager.createVirtualDisplay` + `VirtualDisplayConfig.Builder.setDisplayIdToMirror(srcId)` + `setSurface(호스트 Surface)` | `DisplayMirrorBackend.kt:288, 392` |
| `window_manager` | `IWindowManager.mirrorDisplay(id, SurfaceControl)` → `attachLayer()` reparent/setMatrix/setWindowCrop | `:224, 253` |
| `surface_control` | `SurfaceControl.mirrorDisplay(id)` (static, 히든) → 동일 `attachLayer()` | `:240` |

Samsung 프로필 기본 순서는 `virtual_display → window_manager → surface_control` (`DesktopEnvironment.kt:61`).
**주의:** `configuredMirrorStrategyOverride()` `MirrorService.kt:6902`가 Flutter 설정 `mirror_backend`(기본값 `"virtual_display"`)를 읽어 **단일 전략으로 고정**한다. 사용자가 설정에서 `auto`로 바꾸지 않으면 폴백 체인이 아예 동작하지 않는다. Fold3에서 실험할 때 반드시 `auto`로 두어야 한다.

---

## 2. "One UI 8 이상" 제약은 코드 어디서 강제되는가

### 답: 코드에서 강제되지 않는다. 문서상의 경험적 제약이다.

**버전 상수 가드 전수 조사 결과 (`SDK_INT`/`minSdk` 전체):**

| 위치 | 조건 | Fold3(API 34) 영향 |
| --- | --- | --- |
| `android/app/build.gradle.kts:53` | `minSdk = 29` | 설치 가능 ✅ |
| `DesktopEnvironment.kt:29` | `DeviceMatch.minSdk` 기본값 `29` | — |
| `DeviceProfiles.kt:26` | `samsung_dex` 규칙 = `manufacturers = setOf("samsung")` **SDK 조건 없음** | **매칭됨** ✅ |
| `DeviceProfiles.kt:11` | `samsung_trifold`: `devices=q7mq, minSdk=36` | 해당 없음 |
| `DesktopEnvironment.kt:135` | `aospFreeform`: `platformNative = sdk >= 36` | Samsung 프로필이 먼저 잡히므로 미도달 |
| `DesktopModeConfigurator.kt:48,78` | `SDK ≥ 35` → `wm set-display-engagement-mode` | `configureFreeformWindowing=false`(samsung_dex)라 미실행 |
| `MainActivity.kt:563` | `SDK ≥ 36` → Shizuku 다운로드 링크를 GitHub로 | UI 문구뿐 |
| `setup_page.dart:466` | `sdk >= 36` → 버튼 라벨 | UI 문구뿐 |
| `AndroidAutoMirrorActivity.kt:143` | `SDK < VANILLA_ICE_CREAM(35)` 거부 | **Android Auto 기능만** 차단, 폰 세션 무관 |
| `DextopTileService.kt:31` | `SDK ≥ 34` | 해당 없음 |

즉 `DesktopEnvironmentRegistry.resolve()`는 SM-F926N(Android 14)에서도 **`samsung_dex` 환경을 정상 반환**한다. 앱은 실행되고 세션 시작까지 진입한다.

**"One UI 8" 문자열이 있는 곳은 3군데뿐이고 전부 서술/주석이다:**
- `README.md:61-62` — 호환성 표: "One UI 8 이상 완전 지원 / 그 이전은 제한적이며 호환되지 않을 가능성 높음"
- `MirrorService.kt:6600` — 주석 (HOME 거부 재시도 설명)
- `CHANGELOG.md:113` — "Added complete support for all Galaxy Z Fold series devices running One UI 8"

**Android 16 전용 API 의존은 1건이며 선택 사항이다:**
`DisplayTopologyController` — `IDisplayManager.Stub.TRANSACTION_getDisplayTopology / setDisplayTopology` 트랜잭션 ID를 리플렉션으로 해석(`:332`). 없으면 `isSupported()==false`로 조용히 건너뛴다(`:337`). 호출부(`MirrorService.kt:6554`)도 `runCatching`으로 감싸고 주석에 *"topology activation skipped; mirroring remains active"* 라고 명시.

### 그렇다면 실제 제약의 정체는

`DesktopEnvironmentRegistry.samsungDex()` (`DesktopEnvironment.kt:128`):
```kotlin
DesktopEnvironment(
    "samsung_dex", "Samsung DeX",
    platformManaged = true,              // ← DesktopModeConfigurator가 아무것도 안 함
    temporaryGlobalSettings = emptyMap(),// ← 강제할 설정이 없음
    configureFreeformWindowing = false,  // ← wm set-display-windowing-mode 미실행
    startupMode = OEM_MANAGED,           // ← "OEM이 알아서 한다"
    displayChromeMode = HIDDEN
)
```
`DesktopModeConfigurator.applyForCurrentDevice()` (`:26`)는 `platformManaged`이면 즉시 반환한다. 즉 **삼성 기기에서 Dextop이 데스크톱 모드를 만드는 코드는 0줄**이다. 전부 One UI에 위임되어 있다.

이 위임이 성립하려면 One UI 쪽이 "물리 외부 디스플레이가 아닌 디스플레이에도 덱스 셸을 붙여준다"는 성질을 가져야 한다. 그 성질이 One UI 8부터 생겼다는 것이 이 제약의 실체다. (One UI 8이 덱스를 AOSP Desktop Windowing 위에 재구축했다는 점과 정합 — *이 인과 설명 자체는 저장소 밖 사실에 기반한 추론이며, 저장소가 직접 증명하는 것은 아래 §3의 실패 기록이다.*)

---

## 3. One UI 6.1(Android 14) / SM-F926N 동작 가능성 판정

### 판정: 삼성 덱스 형태로는 **불가능**. 루팅 여부와 무관하지 않지만, 루팅해도 앱 수정 없이는 안 된다.

#### 근거 1 — 동일 하드웨어의 실패 기록이 저장소 안에 있다 (가장 강한 근거)

`docs/wiki/Reported-Devices.md:349-403`, `README.md:86`:

| 항목 | 값 |
| --- | --- |
| 기기 | Galaxy Z Fold3 5G, `SCG11` (au 일본향 — **SM-F926N과 동일 하드웨어**) |
| 소프트웨어 | **Android 15 (API 35) / One UI 7.0** / `SCG11KDS1EZB8` |
| 앱 시작·기기 인식 | ✅ 정상 |
| **Dextop 세션 시작** | ❌ 실패 |
| **VirtualDisplay 미러링** | ❌ |
| **WindowManager 미러링** | ❌ |
| **SurfaceControl 미러링** | ❌ |

내 기기(One UI 6.1 / Android 14)는 이보다 **두 단계 낮은** 버전이다. One UI 7에서 실패한 것이 6.1에서 성공할 근거는 없다.

#### 근거 2 — 앱이 호출하는 API 중 Android 14에 없는 것은 없다

| 앱이 쓰는 것 | Android 14(API 34) 가용성 |
| --- | --- |
| `Settings.Global.overlay_display_devices` (+ `secure`, `should_show_system_decorations` 토큰) | ✅ (AOSP `OverlayDisplayAdapter`, 데코 플래그는 Android 10부터) |
| `IWindowManager.setShouldShowSystemDecors` / `setDisplayImePolicy` / `setIgnoreOrientationRequest` / `setFixedToUserRotation` / `freezeDisplayRotation` | ✅ (코드가 리플렉션으로 시그니처 변화까지 흡수 — `applyDisplayRotation()` `:6736`) |
| `IDisplayManager.createVirtualDisplay` + `VirtualDisplayConfig.Builder.setDisplayIdToMirror` | ✅ (`PixelMirrorFallback.kt:43`이 부재 가능성을 런타임 probe로 처리) |
| `SurfaceControl.mirrorDisplay(int)` / `SurfaceControl.Transaction.setMatrix/setWindowCrop` | ✅ |
| `IInputManager.injectInputEvent` + `InputEvent.setDisplayId` | ✅ |
| `uinput` 쉘 바이너리 | ✅ |
| `Sensor.TYPE_HINGE_ANGLE` (API 30+) / `androidx.window` `FoldingFeature` | ✅ Fold3 지원 |
| `IDisplayManager.get/setDisplayTopology` | ❌ (Android 16) — **선택 사항, 실패해도 세션 유지** |

→ **"빠진 API" 때문에 불가능한 것이 아니다.** 즉 질문 3의 "어떤 API가 빠져서 불가능한지 특정하라"에 대한 정확한 답은: **빠진 것은 앱이 호출하는 API가 아니라, One UI 6.1의 `system_server` 쪽 동작(비물리 디스플레이에 덱스 셸을 붙이는 정책)이다.** 이는 앱 프로세스에서 호출 가능한 표면이 아니라 플랫폼 내부 판정이므로, Shizuku의 shell 권한(uid 2000)으로도, root(uid 0)로도 "없는 기능을 부를" 수는 없다.

#### 근거 3 — 구조적 이유

`samsung_dex` 프로필은 데스크톱 모드를 만들지 않고 관측만 한다(§2). One UI 6.1의 덱스는 `DisplayManager`가 보고하는 디스플레이 타입이 물리 외부(HDMI/DP) 또는 무선 덱스일 때만 기동한다. Dextop이 만드는 디스플레이는 `TYPE_OVERLAY`(=4)이며, `DisplayMirrorBackend.findCreatedDisplay()` `:129`가 명시적으로 `getType() == 4`인 디스플레이를 찾는다. 덱스 입장에서 이 디스플레이는 존재하지 않는 것과 같다.
따라서 `launchHome()` (`:6760`)이 그 디스플레이에서 실패하고 → `retryHomeLaunchWithSystemDecorations()` 1회 재시도 후 → `error("The desktop HOME activity could not be launched")` → `stop()`.

#### 루팅에 대해

부트로더 언락 불가라 루팅은 이미 배제 대상이지만, 명확히 해 둘 필요가 있다: **루팅해도 덱스는 붙지 않는다.** root는 "권한"을 주지 그 버전 프레임워크에 "없는 기능"을 만들어 주지 않는다. One UI 6.1에서 덱스를 오버레이 디스플레이에 붙이려면 `system_server` 자체를 패치해야 하고(Magisk/LSPosed 모듈 수준), 그건 Dextop 포팅이 아니라 별개의 프로젝트다.

---

## 4. 그래도 시도할 수 있는 것 — "덱스" 대신 "AOSP 프리폼 데스크톱"

목표를 **"Fold3 화면 위에, 삼성 덱스가 아닌 AOSP 프리폼 데스크톱을 띄운다"** 로 바꾸면 승산이 생긴다. Dextop에 이미 그 경로가 구현되어 있기 때문이다.

`DesktopEnvironmentRegistry.aospFreeform()` (`DesktopEnvironment.kt:134`)는 SDK < 36일 때:
- `temporaryGlobalSettings` = `AndroidDesktopOverrides.compatibilityValues` (`DesktopEnvironment.kt:87`)
  → `force_resizable_activities=1`, `enable_freeform_support=1`, `force_desktop_mode_on_external_displays=1`
- `configureFreeformWindowing = true` → `DesktopModeConfigurator.configureDisplay()` `:45` 실행
  → `wm set-display-windowing-mode -d <id> 5` (5 = `WINDOWING_MODE_FREEFORM`), 실패 시 `cmd activity_task set-display-windowing-mode`
  → 250ms / 750ms 후 재적용
- `startupMode = COMPAT_WINDOWING`, `displayChromeMode = VISIBLE`

문제는 **Samsung 규칙(`DeviceProfiles.kt:26`)이 SDK 조건 없이 먼저 매칭되어** Fold3를 `samsung_dex`(= 아무것도 안 함)로 보내 버린다는 점이다. 이게 유일하게 "One UI 8 제약"에 근접한 코드상 지점이며, 규칙 하나로 우회 가능하다.

### 제안 패치 설계 (아직 미적용 — 승인 시 진행)

`DeviceProfiles.rules`의 `samsung_trifold` **뒤, `samsung_carrier_model` 앞**에 삽입 (첫 매칭 우선이므로 순서 중요):

```kotlin
// One UI 8 이전 Samsung 빌드는 비물리 디스플레이에 DeX 셸을 붙이지 않는다.
// 플랫폼 위임(OEM_MANAGED) 대신 AOSP 프리폼 경로를 시도한다.
// SDK 상한을 두어 One UI 8 이상 기기의 동작은 절대 바꾸지 않는다.
DesktopEnvironmentRule(
    "samsung_pre_desktop_windowing",
    DeviceMatch(manufacturers = setOf("samsung"), minSdk = 29, maxSdk = 34)
) { identity ->
    DesktopEnvironmentRegistry.aospFreeform(identity).copy(
        id = "samsung_pre_desktop_windowing",
        // 폴백 체인 유지. 다른 기기의 기본 순서는 건드리지 않는다.
        mirrorStrategies = listOf("virtual_display", "window_manager", "surface_control")
    )
}
```

- `maxSdk = 34`로 잘라 One UI 8(API 36) 이상 기기에는 **어떤 영향도 없다**. `docs/ADDING_DEVICE_SUPPORT.en.md`의 "OS 버전 한정 문제에는 minSdk/maxSdk를 설정하라" 규칙 준수.
- `DeviceMatchTest.kt`에 양성(SM-F926N/API 34) + 음성(API 36 삼성, 비삼성) 테스트 추가 필요.
- 함께 필요한 런타임 설정: 앱 설정에서 `mirror_backend`를 **`auto`** 로 (§1-6, 그러지 않으면 `virtual_display` 단일 전략만 시도).

### 이 패치의 성공 확률: 낮음~중간

| 관문 | 전망 |
| --- | --- |
| 오버레이 디스플레이 생성 (`overlay_display_devices`) | 성공 가능성 높음 — 개발자 옵션 "보조 디스플레이 시뮬레이션"과 동일 경로 |
| 미러링 (3전략 중 하나) | **불확실.** SCG11/One UI 7 리포트는 3개 전부 ❌. 다만 그 세션은 그 이전 단계에서 이미 실패했을 수 있어 미러링 자체의 사망 선고인지는 로그 없이는 단정 불가 |
| 프리폼 전환 (`wm set-display-windowing-mode 5`) | **가장 불확실.** 삼성은 WMShell을 포크했고 One UI 6.1에서 AOSP 프리폼 셸이 온전히 남아 있는지 미검증 |
| 태스크바/시스템 UI | 기대하지 말 것. 나와도 AOSP 것이고, 안 나올 가능성이 높다 |
| 노트북 모드·힌지 감지·해상도 자동 전환 | 데스크톱만 뜨면 그대로 동작할 가능성 높음 (§1-5의 모든 API가 Android 14 가용) |

**따라서 패치 이전에 진단부터 하는 것이 정확한 순서다.** 실기기에서 확인할 것:

```sh
# 1) 오버레이 디스플레이 생성 자체가 되는가
adb shell settings put global overlay_display_devices "1920x1080/240,should_show_system_decorations"
adb shell dumpsys display | grep -i -A3 "overlay\|mDisplayId"
adb shell settings put global overlay_display_devices ""

# 2) 프리폼/데스크톱 모드 설정이 살아 있는가
adb shell settings get global force_desktop_mode_on_external_displays
adb shell wm set-display-windowing-mode -d <위에서 얻은 id> 5   # 오류 메시지 확인

# 3) 히든 미러링 API 존재 확인 (앱 설치 후: 설정 → 앱 정보 → 진단 리포트의 probe.* 항목)
```
Dextop을 그냥 설치해 세션 시작을 눌러 보고 **진단 리포트의 `probe.*` / `strategy=... success=...` 라인**을 확보하는 것이 가장 빠르다. 앱은 API 34에서 정상 실행되고, 실패해도 `SessionJournal`이 변경한 설정을 복원한다(`DesktopModeConfigurator.restore()` `:98`).

---

## 5. 다음 단계 선택지

| 옵션 | 내용 | 비고 |
| --- | --- | --- |
| A. 진단 우선 (권장) | Fold3에 Stellar + Dextop 1.4.2 설치 → 세션 시작 시도 → 진단 리포트 확보 | 코드 수정 0. 위 §4 패치의 성공 여부를 사전에 거의 확정 가능 |
| B. 패치 후 빌드 | §4 규칙 추가 + `DeviceMatchTest` + `flutter build apk` | 백업 후 진행. 서명키 없으면 debug 빌드 |
| C. 상류 기여 | 진단 결과를 `device_support.yml` 이슈로 제출 | Fold3는 이미 ❌ 등재됨. 로그 있으면 가치 있음 |

---

## 부록: 파일 역할 요약

| 파일 | 줄수 | 역할 |
| --- | --- | --- |
| `MirrorService.kt` | 7,966 | AccessibilityService. 세션 생명주기, 오버레이 UI, 입력 주입, 노트북 모드, 힌지 감지 — 사실상 앱 본체 |
| `MainActivity.kt` | 992 | Flutter MethodChannel, Stellar/Shizuku 권한 흐름, 상태 보고 |
| `DisplayMirrorBackend.kt` | 563 | 디스플레이 생성 요청 + 3종 미러링 백엔드 |
| `DisplayTopologyController.kt` | 466 | Android 16 토폴로지 API (선택) |
| `DesktopEnvironment.kt` | 156 | `DeviceMatch` / 환경 프로필 정의 |
| `SamsungDesktopSettings.kt` | 178 | 덱스 설정 17키 읽기/쓰기/백업/복원 |
| `DesktopModeConfigurator.kt` | 104 | 프리폼 전환 (삼성에서는 no-op) |
| `PrivilegedAccess.kt` | 41 | Shizuku/Stellar 단일 통로 |
| `InputDispatcher.kt` | 39 | `IInputManager.injectInputEvent` 래퍼 |
| `DeviceProfiles.kt` | 44 | 기기 매칭 규칙 목록 (**패치 지점**) |
| `CapabilityProbe.kt` | 45 | 읽기 전용 런타임 능력 탐지 |
