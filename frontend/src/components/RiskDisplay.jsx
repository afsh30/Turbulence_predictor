import { motion } from 'framer-motion'
import { AlertCircle, CheckCircle, BarChart2 } from 'lucide-react'

function RiskDisplay({ prediction }) {
    if (!prediction) {
        return (
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 0.5 }}
                className="text-center text-blue-200 p-8 border-2 border-dashed border-blue-400/30 rounded-2xl h-full flex items-center justify-center"
            >
                <p>Results will appear here after analysis</p>
            </motion.div>
        )
    }

    const isHighRisk = prediction.turbulence_risk === 1
    const percentage = (prediction.risk_probability * 100).toFixed(1)
    const explanation = prediction.explanation || []

    return (
        <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className={`p-6 rounded-2xl border backdrop-blur-md shadow-xl overflow-hidden ${isHighRisk
                    ? 'bg-red-500/10 border-red-500/50 text-red-100'
                    : 'bg-green-500/10 border-green-500/50 text-green-100'
                }`}
        >
            <div className="flex flex-col items-center gap-4 mb-6">
                {isHighRisk ? (
                    <AlertCircle className="w-16 h-16 text-red-400" />
                ) : (
                    <CheckCircle className="w-16 h-16 text-green-400" />
                )}

                <h2 className="text-3xl font-bold">{prediction.message}</h2>

                <div className="text-center">
                    <p className="text-lg opacity-80">Risk Probability</p>
                    <div className="text-4xl font-bold mt-1">{percentage}%</div>
                </div>

                <div className="w-full bg-black/20 h-4 rounded-full overflow-hidden mt-4">
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${percentage}%` }}
                        transition={{ duration: 1, ease: "easeOut" }}
                        className={`h-full ${isHighRisk ? 'bg-red-500' : 'bg-green-500'}`}
                    />
                </div>
            </div>

            {/* SHAP Explanation Section */}
            {explanation.length > 0 && (
                <div className="mt-6 border-t border-white/10 pt-4">
                    <div className="flex items-center gap-2 mb-4">
                        <BarChart2 size={20} />
                        <h3 className="text-xl font-semibold">How It Works (SHAP)</h3>
                    </div>
                    <p className="text-sm opacity-70 mb-4">
                        See which features pushed the prediction towards Turbulence (+).
                    </p>

                    <div className="space-y-3">
                        {explanation.slice(0, 5).map((item, index) => (
                            <div key={index} className="relative">
                                <div className="flex justify-between text-sm mb-1">
                                    <span>{item.feature}</span>
                                    <span className={item.contribution > 0 ? "text-red-300" : "text-green-300"}>
                                        {item.contribution > 0 ? "+" : ""}{item.contribution.toFixed(2)}
                                    </span>
                                </div>
                                {/* Visual Bar */}
                                <div className="w-full bg-black/20 h-2 rounded-full overflow-hidden flex items-center relative">
                                    {/* Center line */}
                                    <div className="absolute left-1/2 w-0.5 h-full bg-white/30"></div>

                                    {/* Bar */}
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: `${Math.abs(item.contribution) * 50}%` }}
                                        className={`h-full ${item.contribution > 0 ? 'bg-red-400' : 'bg-green-400'} absolute top-0`}
                                        style={{
                                            left: item.contribution > 0 ? '50%' : 'auto',
                                            right: item.contribution < 0 ? '50%' : 'auto'
                                        }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </motion.div>
    )
}

export default RiskDisplay
