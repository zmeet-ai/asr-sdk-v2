package com.abcpen;

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
    private final boolean recall;
    private WebSocketClient wsClient;
    private final ObjectMapper objectMapper = new ObjectMapper();

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
        this(appId, appSecret, printMode, asrType, audioFile, "0", true);
    }

    public AsrClient(String appId, String appSecret, String printMode, String asrType, 
                    String audioFile, String transMode, boolean recall) {
        this.appId = appId;
        this.appSecret = appSecret;
        this.printMode = printMode;
        this.asrType = asrType;
        this.audioFile = audioFile;
        this.transMode = transMode;
        this.recall = recall;
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
                    "&asr_type=%s&trans_mode=%s&target_lang=%s&pd=%s&recall=%s",
                    appId, ts, signa, asrType, transMode, TARGET_LANG, PD, recall);

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
        Map<String, Object> asrJson = objectMapper.readValue(message, HashMap.class);
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
                    wsClient.send(buffer);
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
        if (args.length < 2) {
            System.out.println("Usage: java -jar realtime_asr_voiceid.jar <mode> <args>");
            System.out.println("Modes:");
            System.out.println("  asr <audio_file_path> [appId] [appSecret] [printMode] [asrType] [transMode] [recall]");
            System.out.println("  register <audio_file_path> <speaker_name> [appId] [appSecret]");
            System.out.println("  search <audio_file_path> [appId] [appSecret]");
            System.out.println("  delete-all [appId] [appSecret]");
            System.exit(1);
        }

        String mode = args[0];
        //请向公司商务申请账号
        String appId = "xxx";
        String appSecret = "xxx";
        String serverUrl = "https://audio.abcpen.com";

        switch (mode) {
            case "asr":
                String audioFile = args[1];
                String printMode = args.length > 4 ? args[4] : "typewriter";
                String asrType = args.length > 5 ? args[5] : "word";
                String transMode = args.length > 6 ? args[6] : "0";
                boolean recall = args.length > 7 ? Boolean.parseBoolean(args[7]) : true;
                
                if (args.length > 2) appId = args[2];
                if (args.length > 3) appSecret = args[3];

                AsrClient client = new AsrClient(appId, appSecret, printMode, asrType, audioFile, transMode, recall);
                client.start();
                break;

            case "register":
                if (args.length < 3) {
                    System.out.println("Error: register mode requires audio_file_path and speaker_name");
                    System.exit(1);
                }
                if (args.length > 3) appId = args[3];
                if (args.length > 4) appSecret = args[4];

                VoiceIdClient voiceIdClient = new VoiceIdClient(appId, appSecret, serverUrl);
                voiceIdClient.registerVoice(args[1], args[2], "abcpen", "abcpen");
                break;

            case "search":
                if (args.length > 2) appId = args[2];
                if (args.length > 3) appSecret = args[3];

                voiceIdClient = new VoiceIdClient(appId, appSecret, serverUrl);
                voiceIdClient.searchVoice(args[1], "abcpen", "abcpen");
                break;

            case "delete-all":
                if (args.length > 1) appId = args[1];
                if (args.length > 2) appSecret = args[2];

                voiceIdClient = new VoiceIdClient(appId, appSecret, serverUrl);
                voiceIdClient.deleteAllVoices("abcpen", "abcpen");
                break;

            default:
                System.out.println("Unknown mode: " + mode);
                System.exit(1);
        }
    }
}


