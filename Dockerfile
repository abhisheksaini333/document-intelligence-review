FROM node:18.12.0-bullseye-slim AS frontend
WORKDIR /ui
COPY frontend/package*.json ./
RUN npm ci --ignore-scripts --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM python:3.10.6-slim-bullseye AS ocr
RUN printf 'deb [check-valid-until=no] https://snapshot.debian.org/archive/debian/20221101T000000Z/ bullseye main\n' > /etc/apt/sources.list
RUN apt-get update && apt-get install -y --no-install-recommends build-essential autoconf automake libtool pkg-config libleptonica-dev ca-certificates curl && rm -rf /var/lib/apt/lists/*
ADD https://codeload.github.com/tesseract-ocr/tesseract/tar.gz/refs/tags/5.2.0 /tmp/tesseract.tar.gz
RUN echo 'eba4deb2f92a3f89a6623812074af8c53b772079525b3c263aa70bbf7b748b3c  /tmp/tesseract.tar.gz' | sha256sum -c -
RUN tar -xzf /tmp/tesseract.tar.gz -C /tmp && cd /tmp/tesseract-5.2.0 && ./autogen.sh && ./configure --disable-openmp --disable-shared && make -j2 && make install
ADD https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/65727574dfcd264acbb0c3e07860e4e9e9b22185/eng.traineddata /usr/local/share/tessdata/eng.traineddata

RUN echo '7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2  /usr/local/share/tessdata/eng.traineddata' | sha256sum -c -

FROM ocr AS dependencies
COPY requirements-ops.lock /tmp/requirements-ops.lock
RUN pip install --no-cache-dir --prefix=/install -r /tmp/requirements-ops.lock

FROM python:3.10.6-slim-bullseye
RUN printf 'deb [check-valid-until=no] https://snapshot.debian.org/archive/debian/20221101T000000Z/ bullseye main\n' > /etc/apt/sources.list
RUN apt-get update && apt-get install -y --no-install-recommends liblept5 libgomp1 libstdc++6 fonts-dejavu-core ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=ocr /usr/local/bin/tesseract /usr/local/bin/tesseract
COPY --from=ocr /usr/local/share/tessdata /usr/local/share/tessdata
WORKDIR /app
COPY --from=dependencies /install /usr/local
COPY docreview/ ./docreview/
COPY service.py ./
COPY --from=frontend /ui/dist ./frontend/dist/
RUN chmod -R a+rX /usr/local/share/tessdata && useradd --uid 10001 --create-home reviewer && mkdir /data && chown reviewer:reviewer /data
USER reviewer
ENV OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
EXPOSE 4800
CMD ["python","-m","docreview","serve","--host","0.0.0.0","--port","4800","--data","/data"]
