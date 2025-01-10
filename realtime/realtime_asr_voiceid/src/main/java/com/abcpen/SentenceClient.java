package com.abcpen;

import okhttp3.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.util.concurrent.TimeUnit;

public class SentenceClient {
    private static final Logger LOGGER = LoggerFactory.getLogger(SentenceClient.class);
    private final String appId;
    private final String appSecret;
    private final String serverUrl;
    private final OkHttpClient httpClient;

    public SentenceClient(String appId, String appSecret, String serverUrl) {
        this.appId = appId;
        this.appSecret = appSecret;
        this.serverUrl = serverUrl;
        this.httpClient = new OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build();
    }

    public void recognizeSentence(String audioPath, String language, boolean fast) {
        try {
            String[] signatureData = SignatureUtil.generateSignature(appId, appSecret);
            String url = serverUrl + "/sentence/v2/sentence";

            RequestBody requestBody = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("audio_file", new File(audioPath).getName(),
                    RequestBody.create(new File(audioPath), MediaType.parse("audio/*")))
                .addFormDataPart("language", language)
                .addFormDataPart("fast", String.valueOf(fast))
                .addFormDataPart("voiceprint_enabled", "true")
                .addFormDataPart("voiceprint_org_id", appId)
                .addFormDataPart("voiceprint_tag_id", appId)
                .build();

            Request request = new Request.Builder()
                .url(url)
                .addHeader("X-App-Key", appId)
                .addHeader("X-App-Signature", signatureData[0])
                .addHeader("X-Timestamp", signatureData[1])
                .post(requestBody)
                .build();

            try (Response response = httpClient.newCall(request).execute()) {
                String result = response.body().string();
                LOGGER.info("Sentence recognition result: {}", result);
            }
        } catch (Exception e) {
            LOGGER.error("Failed to recognize sentence", e);
        }
    }
}
