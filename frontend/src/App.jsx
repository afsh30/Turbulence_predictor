import { useState } from 'react'
import TurbulenceForm from './components/TurbulenceForm'
import RiskDisplay from './components/RiskDisplay'
import { motion } from 'framer-motion'
import axios from 'axios'
import { Plane, Wind } from 'lucide-react'

function App() {
    const [prediction, setPrediction] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const handlePredict = async (data) => {
        setLoading(true)
        setError(null)
        setPrediction(null)
        try {
            // Assuming backend is running on localhost:8000
            const response = await axios.post('http://127.0.0.1:8000/predict', data)
            setPrediction(response.data)
        } catch (err) {
            console.error(err)
            setError('Failed to get prediction. Ensure backend is running.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex flex-col items-center justify-center p-4">
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center mb-8"
            >
                <div className="flex items-center justify-center gap-3 mb-2">
                    <Plane className="w-10 h-10" />
                    <h1 className="text-4xl font-bold">Turbulence Predictor</h1>
                </div>
                <p className="text-blue-100">AI-Powered Flight Safety Analysis</p>
            </motion.div>

            <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-6">
                <TurbulenceForm onPredict={handlePredict} loading={loading} />

                <div className="flex flex-col justify-center">
                    {error && (
                        <div className="bg-red-500/20 border border-red-500 text-red-100 p-4 rounded-xl mb-4 text-center">
                            {error}
                        </div>
                    )}
                    <RiskDisplay prediction={prediction} />
                </div>
            </div>
        </div>
    )
}

export default App
