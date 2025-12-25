import { FC } from 'react'

interface SeverityBadgeProps {
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
  size?: 'sm' | 'md' | 'lg'
}

const SeverityBadge: FC<SeverityBadgeProps> = ({ severity, size = 'md' }) => {
  const severityColors = {
    critical: 'bg-red-600 text-white',
    high: 'bg-orange-500 text-white',
    medium: 'bg-yellow-500 text-black',
    low: 'bg-green-600 text-white',
    info: 'bg-blue-600 text-white',
  }

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-2 text-base',
  }

  return (
    <span
      className={`inline-block rounded font-semibold ${severityColors[severity]} ${sizeClasses[size]}`}
    >
      {severity.charAt(0).toUpperCase() + severity.slice(1)}
    </span>
  )
}

export default SeverityBadge
