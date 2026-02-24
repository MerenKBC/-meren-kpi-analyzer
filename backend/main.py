from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import pandas as pd
import io
from analyzer import SalesAnalyzer
from visualizer import SalesVisualizer
from reporter import SalesReporter

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for analysis (in a real app, this would be a database or session)
current_data = {"df": None}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Desteklenmeyen dosya formatı.")
        
        current_data["df"] = df
        analyzer = SalesAnalyzer(df)
        visualizer = SalesVisualizer(analyzer)
        
        return {
            "message": "Dosya başarıyla yüklendi.",
            "kpis": analyzer.get_kpis(),
            "charts": {
                "trend": visualizer.generate_trend_chart(),
                "category": visualizer.generate_category_chart()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/report")
async def get_report():
    if current_data["df"] is None:
        raise HTTPException(status_code=404, detail="Önce veri yüklemelisiniz.")
    
    analyzer = SalesAnalyzer(current_data["df"])
    visualizer = SalesVisualizer(analyzer)
    reporter = SalesReporter(analyzer, visualizer)
    
    pdf_content = reporter.generate_pdf()
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=satis_raporu.pdf"}
    )

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
