package com.abcpen;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.util.concurrent.TimeUnit;

import okhttp3.*;

public class VoiceIdClient {
    private static final Logger LOGGER = LoggerFactory.getLogger(VoiceIdClient.class);
    private final String appId;
    private final String appSecret;
    private final String serverUrl;
    private final OkHttpClient httpClient;

    public VoiceIdClient(String appId, String appSecret, String serverUrl) {
        this.appId = appId;
        this.appSecret = appSecret;
        this.serverUrl = serverUrl;
        this.httpClient = new OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build();
    }

    public void registerVoice(String audioPath, String speakerName, String orgId, String tagId) {
        try {
            String[] signatureData = SignatureUtil.generateSignature(appId, appSecret);
            String url = serverUrl + "/voiceid/register/v2";

            RequestBody requestBody = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("audio", new File(audioPath).getName(),
                    RequestBody.create(new File(audioPath), MediaType.parse("audio/*")))
                .addFormDataPart("spk_name", speakerName)
                .addFormDataPart("org_id", orgId)
                .addFormDataPart("tag_id", tagId)
                .addFormDataPart("denoise_audio", "0")
                .addFormDataPart("audio_preprocess", "false")
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
                LOGGER.info("Voice register result: {}", result);
            }
        } catch (Exception e) {
            LOGGER.error("Failed to register voice", e);
        }
    }

    public void searchVoice(String audioPath, String orgId, String tagId) {
        try {
            String[] signatureData = SignatureUtil.generateSignature(appId, appSecret);
            String url = serverUrl + "/voiceid/recognize/v2";

            RequestBody requestBody = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("audio", new File(audioPath).getName(),
                    RequestBody.create(new File(audioPath), MediaType.parse("audio/*")))
                .addFormDataPart("org_id", orgId)
                .addFormDataPart("tag_id", tagId)
                .addFormDataPart("denoise_audio", "0")
                .addFormDataPart("audio_preprocess", "false")
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
                LOGGER.info("Voice search result: {}", result);
            }
        } catch (Exception e) {
            LOGGER.error("Failed to search voice", e);
        }
    }

    public void deleteAllVoices(String orgId, String tagId) {
        try {
            String[] signatureData = SignatureUtil.generateSignature(appId, appSecret);
            String url = serverUrl + "/voiceid/delete-speakers?org_id=" + orgId + "&tag_id=" + tagId;

            Request request = new Request.Builder()
                .url(url)
                .addHeader("X-App-Key", appId)
                .addHeader("X-App-Signature", signatureData[0])
                .addHeader("X-Timestamp", signatureData[1])
                .get()
                .build();

            try (Response response = httpClient.newCall(request).execute()) {
                String result = response.body().string();
                LOGGER.info("Delete all voices result: {}", result);
            }
        } catch (Exception e) {
            LOGGER.error("Failed to delete all voices", e);
        }
    }

    public void deleteSpeaker(String speakerName, String orgId, String tagId) {
        try {
            String[] signatureData = SignatureUtil.generateSignature(appId, appSecret);
            String url = serverUrl + "/voiceid/delete-speakers?speaker=" + speakerName 
                + "&org_id=" + orgId + "&tag_id=" + tagId;

            Request request = new Request.Builder()
                .url(url)
                .addHeader("X-App-Key", appId)
                .addHeader("X-App-Signature", signatureData[0])
                .addHeader("X-Timestamp", signatureData[1])
                .get()
                .build();

            try (Response response = httpClient.newCall(request).execute()) {
                String result = response.body().string();
                LOGGER.info("Delete speaker result: {}", result);
            }
        } catch (Exception e) {
            LOGGER.error("Failed to delete speaker", e);
        }
    }

    public void countVoices(String orgId, String tagId) {
        try {
            String[] signatureData = SignatureUtil.generateSignature(appId, appSecret);
            String url = serverUrl + "/voiceid/count?org_id=" + orgId + "&tag_id=" + tagId;

            Request request = new Request.Builder()
                .url(url)
                .addHeader("X-App-Key", appId)
                .addHeader("X-App-Signature", signatureData[0])
                .addHeader("X-Timestamp", signatureData[1])
                .get()
                .build();

            try (Response response = httpClient.newCall(request).execute()) {
                String result = response.body().string();
                LOGGER.info("Voice count result: {}", result);
            }
        } catch (Exception e) {
            LOGGER.error("Failed to count voices", e);
        }
    }
}