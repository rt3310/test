# --- 단계 1: nGrinder 3.5.9 소스 빌드 ---
FROM adoptopenjdk/openjdk11:alpine-slim AS build-stage

# 빌드에 필요한 도구 설치
RUN apk add --no-cache git bash

WORKDIR /workspace
RUN git clone https://github.com/naver/ngrinder.git .

# ngrinder-core/build.gradle 수정 (JNA/OSHI 버전 강제 업데이트)
RUN sed -i 's/group: "com.github.oshi", name: "oshi-core", version: "6.1.6"/group: "com.github.oshi", name: "oshi-core", version: "6.4.10"/g' ngrinder-core/build.gradle && \
    sed -i 's/group: "net.java.dev.jna", name: "jna", version: "5.6.0"/group: "net.java.dev.jna", name: "jna", version: "5.14.0"/g' ngrinder-core/build.gradle && \
    sed -i 's/group: "net.java.dev.jna", name: "jna-platform", version: "5.6.0"/group: "net.java.dev.jna", name: "jna-platform", version: "5.14.0"/g' ngrinder-core/build.gradle

# gradlew 실행 및 빌드 (테스트 제외)
RUN chmod +x ./gradlew
RUN ./gradlew :ngrinder-controller:build -x test

# --- 단계 2: 실행 이미지 생성 ---
FROM adoptopenjdk/openjdk11:alpine-jre

# 빌드 결과물 복사
COPY --from=build-stage /workspace/ngrinder-controller/build/libs/ngrinder-controller-*.war /opt/ngrinder-controller.war

# 환경 설정 및 메모리 할당
ENV JAVA_OPTS="-Duser.home=/opt/ngrinder-controller -Xmx2048m"
EXPOSE 80 16001 12000-12009

ENTRYPOINT ["sh", "-c", "java ${JAVA_OPTS} -jar /opt/ngrinder-controller.war --port 80"]
