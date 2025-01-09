package com.abcpen;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import io.github.cdimascio.dotenv.Dotenv;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import java.util.Arrays;

/**
 * AsrClient handles real-time audio streaming and speech recognition.
 */
public class AsrClient {
    private static final Logger LOGGER = LoggerFactory.getLogger(AsrClient.class);
    private static final int SAMPLE_RATE = 16000;
    private static final int NUM_CHANNEL = 1;
    private static final int NUM_QUANTIFY = 16;
    private static final double TIME_PER_CHUNK = 0.2;
    private static final int BYTES_PER_CHUNK =
            (int) (SAMPLE_RATE * NUM_QUANTIFY * TIME_PER_CHUNK * NUM_CHANNEL / 8);
    private static final long SLEEP_TIME_DURATION = 50;
    private static final int MILLISECONDS_PER_SECOND = 1000;
    private static final String TARGET_LANG = "ru";
    private static final String PD = "court";

    private final String appId;
    private final String appSecret;
    private final String printMode;
    private final String asrType;
    private final String audioFile;
    private final String transMode;
    private WebSocketClient wsClient;
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final String voiceprint;
    private final String voiceprintOrgId;
    private final String voiceprintTagId;
    private final String wordTime;
    private final String metadata;

    /**
     * Constructs an AsrClient with the specified parameters.
     *
     * @param appId Application ID for authentication
     * @param appSecret Application secret for authentication
     * @param printMode Output mode ("typewriter" or "json")
     * @param asrType Recognition type ("word" or "sentence")
     * @param audioFile Path to the audio file
     */
    public AsrClient(String appId, String appSecret, String printMode, String asrType, String audioFile) {
        this(appId, appSecret, printMode, asrType, audioFile, "0", "1", appId, appId, "0", getDefaultMetadata());
    }

    public AsrClient(String appId, String appSecret, String printMode, String asrType, 
                    String audioFile, String transMode) {
        this(appId, appSecret, printMode, asrType, audioFile, transMode, "1", appId, appId, "0", getDefaultMetadata());
    }

    public AsrClient(String appId, String appSecret, String printMode, String asrType, 
                    String audioFile, String transMode,
                    String voiceprint, String voiceprintOrgId, String voiceprintTagId, String wordTime) {
        this(appId, appSecret, printMode, asrType, audioFile, transMode,
             voiceprint, voiceprintOrgId, voiceprintTagId, wordTime, getDefaultMetadata());
    }

    public AsrClient(String appId, String appSecret, String printMode, String asrType, 
                    String audioFile, String transMode,
                    String voiceprint, String voiceprintOrgId, String voiceprintTagId, 
                    String wordTime, String metadata) {
        this.appId = appId;
        this.appSecret = appSecret;
        this.printMode = printMode;
        this.asrType = asrType;
        this.audioFile = audioFile;
        this.transMode = transMode;
        this.voiceprint = voiceprint;
        this.voiceprintOrgId = voiceprintOrgId;
        this.voiceprintTagId = voiceprintTagId;
        this.wordTime = wordTime;
        this.metadata = metadata;
    }

    /**
     * Generates authentication signature.
     *
     * @return Array containing signature and timestamp
     * @throws IllegalStateException if signature generation fails
     */
    private String[] generateSignature() {
        try {
            String ts = String.valueOf(System.currentTimeMillis() / MILLISECONDS_PER_SECOND);
            String baseString = appId + ts;

            MessageDigest md5 = MessageDigest.getInstance("MD5");
            byte[] md5Bytes = md5.digest(baseString.getBytes(StandardCharsets.UTF_8));
            String md5Hex = bytesToHex(md5Bytes);

            Mac hmacSha1 = Mac.getInstance("HmacSHA1");
            SecretKeySpec secretKey = new SecretKeySpec(
                    appSecret.getBytes(StandardCharsets.UTF_8), "HmacSHA1");
            hmacSha1.init(secretKey);
            byte[] hmacBytes = hmacSha1.doFinal(md5Hex.getBytes(StandardCharsets.UTF_8));
            String signa = Base64.getEncoder().encodeToString(hmacBytes);

            return new String[]{signa, ts};
        } catch (NoSuchAlgorithmException | InvalidKeyException e) {
            throw new IllegalStateException("Failed to generate signature", e);
        }
    }

    /**
     * Converts byte array to hexadecimal string.
     *
     * @param bytes Byte array to convert
     * @return Hexadecimal string representation
     */
    private String bytesToHex(byte[] bytes) {
        StringBuilder result = new StringBuilder();
        for (byte b : bytes) {
            result.append(String.format("%02x", b));
        }
        return result.toString();
    }

    /**
     * Starts the ASR client and establishes WebSocket connection.
     */
    public void start() {
        try {
            String[] signatureData = generateSignature();
            String signa = URLEncoder.encode(signatureData[0], StandardCharsets.UTF_8.toString());
            String ts = signatureData[1];

            String wsUrl = String.format(
                    "wss://audio.abcpen.com:8443/asr-realtime/v2/ws?appid=%s&ts=%s&signa=%s" +
                    "&asr_type=%s&trans_mode=%s&target_lang=%s&pd=%s" +
                    "&voiceprint=%s&voiceprint_org_id=%s&voiceprint_tag_id=%s&word_time=%s&metadata=%s",
                    appId, ts, signa, asrType, transMode, TARGET_LANG, PD,
                    voiceprint, voiceprintOrgId, voiceprintTagId, wordTime,
                    URLEncoder.encode(metadata, StandardCharsets.UTF_8.toString()));
            System.out.println(wsUrl);
            wsClient = new WebSocketClient(new URI(wsUrl)) {
                @Override
                public void onOpen(ServerHandshake handshakedata) {
                    LOGGER.info("Connected to ASR server");
                    startSendingAudio();
                }

                @Override
                public void onMessage(String message) {
                    try {
                        processMessage(message);
                    } catch (IOException e) {
                        LOGGER.error("Error processing message: {}", e.getMessage());
                    }
                }

                @Override
                public void onClose(int code, String reason, boolean remote) {
                    LOGGER.info("Connection closed: {}", reason);
                }

                @Override
                public void onError(Exception ex) {
                    LOGGER.error("WebSocket error: {}", ex.getMessage());
                }
            };

            wsClient.connect();
        } catch (IllegalStateException | URISyntaxException | UnsupportedEncodingException e) {
            LOGGER.error("Failed to start client: {}", e.getMessage());
        }
    }

    /**
     * Processes incoming WebSocket messages.
     *
     * @param message The received message
     * @throws IOException if message processing fails
     */
    private void processMessage(String message) throws IOException {
        Map<String, Object> asrJson = objectMapper.readValue(message, new TypeReference<Map<String, Object>>() {});
        boolean isFinal = (boolean) asrJson.getOrDefault("is_final", false);
        int segId = (int) asrJson.getOrDefault("seg_id", 0);
        String asr = (String) asrJson.getOrDefault("asr", "");
        String type = (String) asrJson.getOrDefault("type", "");

        if ("typewriter".equals(printMode)) {
            if ("asr".equals(type)) {
                if (isFinal) {
                    System.out.printf("\r%d:%s%n", segId, asr);
                } else {
                    System.out.printf("\r%d:%s", segId, asr);
                }
            }
        } else {
            if (isFinal) {
                LOGGER.warn(asrJson.toString());
            } else {
                LOGGER.info(asrJson.toString());
            }
        }
    }

    /**
     * Starts sending audio data to the server.
     */
    private void startSendingAudio() {
        new Thread(() -> {
            try (FileInputStream fis = new FileInputStream(new File(audioFile))) {
                byte[] buffer = new byte[BYTES_PER_CHUNK];
                int bytesRead;

                while ((bytesRead = fis.read(buffer)) != -1) {
                    wsClient.send(bytesRead == buffer.length ? buffer : Arrays.copyOf(buffer, bytesRead));
                    Thread.sleep(SLEEP_TIME_DURATION);
                }

                wsClient.send(new byte[0]);
            } catch (IOException | InterruptedException e) {
                LOGGER.error("Error sending audio: {}", e.getMessage());
            }
        }).start();
    }

    /**
     * Main method to demonstrate usage of AsrClient.
     *
     * @param args Command line arguments
     */
    public static void main(String[] args) {
        // 加载 .env 文件
        Dotenv dotenv = null;
        try {
            dotenv = Dotenv.load();
        } catch (Exception e) {
            LOGGER.error("Failed to load .env file: {}", e.getMessage());
        }

        // 从环境变量获取 appId 和 appSecret
        String defaultAppId = dotenv != null ? dotenv.get("ZMEET_APP_ID") : System.getenv("ZMEET_APP_ID");
        String defaultAppSecret = dotenv != null ? dotenv.get("ZMEET_APP_SECRET") : System.getenv("ZMEET_APP_SECRET");

        if (defaultAppId == null || defaultAppSecret == null) {
            LOGGER.error("Missing required environment variables: ZMEET_APP_ID or ZMEET_APP_SECRET");
            System.exit(1);
        }

        Options options = new Options();
        
        // 基础选项
        options.addOption(Option.builder("m")
                .longOpt("mode")
                .desc("运行模式: asr, register, search, delete-all, delete-speaker, count-voices")
                .hasArg()
                .required()
                .build());
                
        options.addOption(Option.builder("f")
                .longOpt("audio-file")
                .desc("音频文件路径")
                .hasArg()
                .build());
                
        // ASR相关选项
        options.addOption(Option.builder("p")
                .longOpt("print-mode")
                .desc("打印模式: typewriter 或 json")
                .hasArg()
                .build());
        options.addOption(Option.builder("t")
                .longOpt("asr-type")
                .desc("识别类型: word 或 sentence")
                .hasArg()
                .build());
        options.addOption(Option.builder()
                .longOpt("trans-mode")
                .desc("翻译模式")
                .hasArg()
                .build());
        options.addOption(Option.builder()
                .longOpt("voiceprint")
                .desc("声纹识别开关")
                .hasArg()
                .build());
        
        // 声纹识别相关选项
        options.addOption(Option.builder("n")
                .longOpt("speaker-name")
                .desc("说话人姓名")
                .hasArg()
                .build());
        
        try {
            CommandLineParser parser = new DefaultParser();
            CommandLine cmd = parser.parse(options, args);
            
            String mode = cmd.getOptionValue("m");
            String defaultAudioFile = "../dataset/asr/1006_20241223_081645_full_audio.wav";
            String serverUrl = "https://voiceid.abcpen.com:8443";

            switch (mode) {
                case "asr":
                    String audioFile = cmd.getOptionValue("f", defaultAudioFile);
                    String printMode = cmd.getOptionValue("p", "typewriter");
                    String asrType = cmd.getOptionValue("t", "word");
                    String transMode = cmd.getOptionValue("trans-mode", "0");
                    String voiceprint = cmd.getOptionValue("voiceprint", "1");
                    String voiceprintOrgId = defaultAppId;
                    String voiceprintTagId = defaultAppId;
                    String wordTime = "0";

                    AsrClient client = new AsrClient(defaultAppId, defaultAppSecret, printMode, 
                        asrType, audioFile, transMode,
                        voiceprint, voiceprintOrgId, voiceprintTagId, wordTime);
                    client.start();
                    break;

                case "register":
                    String registerAudioFile = cmd.getOptionValue("f");
                    String speakerName = cmd.getOptionValue("n");
                    if (registerAudioFile == null || speakerName == null) {
                        throw new ParseException("register 模式需要指定音频文件(-f)和说话人姓名(-n)");
                    }
                    VoiceIdClient registerClient = new VoiceIdClient(defaultAppId, defaultAppSecret, serverUrl);
                    registerClient.registerVoice(registerAudioFile, speakerName, defaultAppId, defaultAppId);
                    break;

                case "search":
                    String searchAudioFile = cmd.getOptionValue("f");
                    if (searchAudioFile == null) {
                        throw new ParseException("search 模式需要指定音频文件(-f)");
                    }
                    VoiceIdClient searchClient = new VoiceIdClient(defaultAppId, defaultAppSecret, serverUrl);
                    searchClient.searchVoice(searchAudioFile, defaultAppId, defaultAppId);
                    break;

                case "delete-all":
                    VoiceIdClient deleteClient = new VoiceIdClient(defaultAppId, defaultAppSecret, serverUrl);
                    deleteClient.deleteAllVoices(defaultAppId, defaultAppId);
                    break;

                case "delete-speaker":
                    String deleteSpeakerName = cmd.getOptionValue("n");
                    if (deleteSpeakerName == null) {
                        throw new ParseException("delete-speaker 模式需要指定说话人姓名(-n)");
                    }
                    VoiceIdClient deleteSpeakerClient = new VoiceIdClient(defaultAppId, defaultAppSecret, serverUrl);
                    deleteSpeakerClient.deleteSpeaker(deleteSpeakerName, defaultAppId, defaultAppId);
                    break;

                case "count-voices":
                    VoiceIdClient countClient = new VoiceIdClient(defaultAppId, defaultAppSecret, serverUrl);
                    countClient.countVoices(defaultAppId, defaultAppId);
                    break;

                default:
                    throw new ParseException("未知的模式: " + mode);
            }
            
        } catch (ParseException e) {
            System.err.println("参数错误: " + e.getMessage());
            HelpFormatter formatter = new HelpFormatter();
            formatter.printHelp("AsrClient", options);
            System.exit(1);
        }
    }

    private static String getDefaultMetadata() {
        try {
            Map<String, String> metadata = new HashMap<>();
            metadata.put("user_id", "1234567890");
            metadata.put("user_name", "John Doe");
            metadata.put("user_email", "john.doe@example.com");
            metadata.put("user_phone", "1234567890");
            metadata.put("user_role", "student");
            metadata.put("user_class", "1001");
            metadata.put("user_school", "ABC School");
            metadata.put("user_grade", "6");
            
            return new ObjectMapper().writeValueAsString(metadata);
        } catch (Exception e) {
            LOGGER.error("Failed to create default metadata: {}", e.getMessage());
            return "{}";
        }
    }
}


