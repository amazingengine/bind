cp .env.example .env

docker compose exec backend uvicorn main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 900
docker compose exec frontend npm run start

# dev
docker compose -f docker-compose.dev.yml up -d --build

# production
docker compose up -d

https://localhost/
http://localhost/

---

### Google Analytics 設定方法

`GA_MEASUREMENT_ID` (測定ID) の確認方法

これはGoogle Analytics 4 (GA4) のプロパティを識別するためのIDで、通常 G-XXXXXXXXXX の形式をしています。

1.  Google Analyticsにログインします。
2.  左下の **[管理]** (歯車アイコン) をクリックします。
3.  **[プロパティ]** 列で、該当するGA4プロパティを選択します。
4.  **[データストリーム]** をクリックします。
5.  **[ウェブ]** を選択し、該当するウェブデータストリームをクリックします。
6.  ストリームの詳細画面に表示されている **[測定ID]** が `GA_MEASUREMENT_ID` です。

`GA_API_SECRET` (API Secret) の確認方法

これはGA4のMeasurement Protocolを使用する際に必要となる秘密鍵です。

1.  上記 `GA_MEASUREMENT_ID` を確認したデータストリームの詳細画面を開きます。
2.  **[Measurement Protocol API のシークレット]** セクションまでスクロールします。
3.  **[作成]** ボタンをクリックして新しいシークレットを作成するか、既存のシークレットを使用します。
4.  作成されたシークレットの値が `GA_API_SECRET` です。

これらの値は機密情報ですので、`.env` ファイルや環境変数として安全に管理してください。
