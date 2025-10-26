```mermaid
graph TD
    A[スタート] --> B[initialize関数を呼び出し、GPIOとPWMを設定]
    B --> C{pullup_input.value() == 1 ?}
    
    C -- YES --> D[MODE_LEDを消灯 (duty_u16(0))]
    D --> Z[メイン処理終了 (別モード)]

    C -- NO --> E[WLANをOFFにし、monitor_pir_sensor関数を呼び出し];
    E --> F{PIRセンサの状態を監視 (無限ループ)};
    
    F --> G{PIRセンサの値 (pir_state) は 1 か？};

    %% センサ HIGH の処理 (pir_state == 1)
    G -- YES (検出) --> H{pir_high_start は None か？};
    H -- YES --> I[pir_high_start に現在時刻を設定];
    H -- NO --> K;

    I --> K;
    K[pir_low_start をリセット (None)];

    K --> L{HIGH状態が4000ms以上継続 & led_state == 0 か？};
    L -- YES --> M[LEDを80%で点灯 (set_led_brightness(80))];
    M --> N[入店メロディを再生 (play_entry_melody())];
    N --> O[led_state = 1 に設定];
    O --> P;
    L -- NO --> P;

    %% センサ LOW の処理 (pir_state == 0)
    G -- NO (非検出) --> Q{pir_low_start は None か？};
    Q -- YES --> R[pir_low_start に現在時刻を設定];
    Q -- NO --> S;

    R --> S;
    S[pir_high_start をリセット (None)];

    S --> T{LOW状態が10000ms以上継続 & led_state == 1 か？};
    T -- YES --> U[LEDを消灯 (set_led_brightness(0))];
    U --> V[退店メロディを再生 (play_exit_melody())];
    V --> W[ブザーを停止];
    W --> X[led_state = 0 に設定];
    X --> P;
    T -- NO --> P;
    
    %% ループの終点
    P[0.5秒待機 (time.sleep(0.5))] --> F;

    %% スタイルの適用
    style M fill:#f9f,stroke:#333
    style U fill:#f9f,stroke:#333
    style N fill:#ccf,stroke:#333
    style V fill:#ccf,stroke:#333
```