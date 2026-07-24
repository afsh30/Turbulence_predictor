import { useState } from 'react'
import { motion } from 'framer-motion'
import { Send, Wind, Thermometer, Droplets, Gauge, ArrowUp } from 'lucide-react'

function TurbulenceForm({ onPredict, loading }) {
    const [formData, setFormData] = useState({
        wind_speed: 8,
        wind_gust: 10,
        temperature: 15,
        pressure: 1013,
        humidity: 60,
        upper_wind_speed: 13,
        temp_gradient: 6
    })

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: parseFloat(e.target.value)
        })
    }

    const handleSubmit = (e) => {
        e.preventDefault()
        onPredict(formData)
    }

    const inputs = [
        { label: 'Wind Speed (m/s)', name: 'wind_speed', icon: Wind, step: 0.1 },
        { label: 'Wind Gust (m/s)', name: 'wind_gust', icon: Wind, step: 0.1 },
        { label: 'Temperature (°C)', name: 'temperature', icon: Thermometer, step: 0.1 },
        { label: 'Pressure (hPa)', name: 'pressure', icon: Gauge, step: 1 },
        { label: 'Humidity (%)', name: 'humidity', icon: Droplets, min: 0, max: 100, step: 1 },
        { label: 'Upper Wind (m/s)', name: 'upper_wind_speed', icon: Wind, step: 0.1 },
        { label: 'Temp Gradient', name: 'temp_gradient', icon: Thermometer, step: 0.1 },
    ]

    return (
        <motion.form
            onSubmit={handleSubmit}
            className="bg-white/10 backdrop-blur-md p-8 rounded-2xl border border-white/20 shadow-xl"
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
        >
            <h3 className="text-xl font-semibold mb-6 text-white border-b border-white/10 pb-2">Flight Parameters</h3>

            <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2 custom-scrollbar">
                {inputs.map((input) => (
                    <div key={input.name}>
                        <label className="flex items-center gap-2 text-sm text-blue-200 mb-1">
                            <input.icon size={16} />
                            {input.label}
                        </label>
                        <input
                            type="number"
                            name={input.name}
                            value={formData[input.name]}
                            onChange={handleChange}
                            step={input.step}
                            className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-400 focus:bg-black/30 transition-colors"
                        />
                    </div>
                ))}
            </div>

            <button
                type="submit"
                disabled={loading}
                className="w-full mt-8 bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-6 rounded-xl transition-all transform hover:scale-[1.02] flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {loading ? (
                    <span className="animate-spin">⏳</span>
                ) : (
                    <>
                        Analyze Risk <Send size={18} />
                    </>
                )}
            </button>
        </motion.form>
    )
}

export default TurbulenceForm
