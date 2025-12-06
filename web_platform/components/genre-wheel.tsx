"use client"

import { useState } from "react"
import type { GenreTreeNode } from "@/lib/api"
import { motion, AnimatePresence } from "framer-motion"

interface GenreWheelProps {
  genres: GenreTreeNode[]
  onSelect: (node: GenreTreeNode, path: GenreTreeNode[]) => void
}

export function GenreWheel({ genres, onSelect }: GenreWheelProps) {
  const [expandedGenre, setExpandedGenre] = useState<string | null>(null)
  const [expandedSubGenre, setExpandedSubGenre] = useState<string | null>(null)
  const [hoveredGenre, setHoveredGenre] = useState<string | null>(null)

  const radius = 220
  const centerX = 500
  const centerY = 500
  const totalSize = 1000

  const getCameraOffset = () => {
    if (!expandedGenre) return { x: 0, y: 0 }

    const genreIndex = genres.findIndex((g) => g.id === expandedGenre)
    if (genreIndex === -1) return { x: 0, y: 0 }

    const angle = (genreIndex / genres.length) * 2 * Math.PI - Math.PI / 2
    // Zoom out more when sub-sub genres are shown
    const offsetDistance = expandedSubGenre ? 120 : 50

    return {
      x: -Math.cos(angle) * offsetDistance,
      y: -Math.sin(angle) * offsetDistance,
    }
  }

  const cameraOffset = getCameraOffset()

  const handleGenreClick = (genre: GenreTreeNode) => {
    if (expandedGenre === genre.id) {
      onSelect(genre, [genre])
    } else if (genre.children && genre.children.length > 0) {
      setExpandedGenre(genre.id)
      setExpandedSubGenre(null)
    } else {
      onSelect(genre, [genre])
    }
  }

  const handleSubGenreClick = (parent: GenreTreeNode, child: GenreTreeNode) => {
    if (expandedSubGenre === child.id) {
      onSelect(child, [parent, child])
    } else if (child.children && child.children.length > 0) {
      setExpandedSubGenre(child.id)
    } else {
      onSelect(child, [parent, child])
    }
  }

  const handleSubSubGenreClick = (parent: GenreTreeNode, child: GenreTreeNode, grandchild: GenreTreeNode) => {
    onSelect(grandchild, [parent, child, grandchild])
  }

  const calculatePositions = (count: number, baseAngle: number, spread: number, baseRadius: number) => {
    const positions = []
    const arcLength = spread
    const angleStep = arcLength / Math.max(1, count - 1)

    for (let i = 0; i < count; i++) {
      const offset = i - (count - 1) / 2
      const angle = baseAngle + offset * angleStep
      const x = centerX + baseRadius * Math.cos(angle)
      const y = centerY + baseRadius * Math.sin(angle)
      positions.push({ angle, x, y })
    }

    return positions
  }

  return (
    <div className="relative flex items-center justify-center overflow-hidden">
      <motion.div
        animate={{
          x: cameraOffset.x,
          y: cameraOffset.y,
        }}
        transition={{
          type: "spring",
          stiffness: 150,
          damping: 25,
          mass: 0.8,
        }}
      >
        <svg
          width={totalSize}
          height={totalSize}
          className="overflow-visible"
          viewBox={`0 0 ${totalSize} ${totalSize}`}
        >
          <g className="lines-layer">
            {genres.map((genre, index) => {
              const angle = (index / genres.length) * 2 * Math.PI - Math.PI / 2
              const x = centerX + radius * Math.cos(angle)
              const y = centerY + radius * Math.sin(angle)
              const isExpanded = expandedGenre === genre.id

              return (
                <motion.line
                  key={`line-${genre.id}`}
                  x1={centerX}
                  y1={centerY}
                  x2={x}
                  y2={y}
                  stroke="#8D6E63"
                  strokeWidth={isExpanded ? 3 : 2}
                  strokeDasharray="4 4"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                />
              )
            })}

            {/* Sub-genre lines */}
            {genres.map((genre, index) => {
              const mainAngle = (index / genres.length) * 2 * Math.PI - Math.PI / 2
              const mainX = centerX + radius * Math.cos(mainAngle)
              const mainY = centerY + radius * Math.sin(mainAngle)
              const isExpanded = expandedGenre === genre.id

              if (!isExpanded || !genre.children) return null

              const subPositions = calculatePositions(genre.children.length, mainAngle, 1.2, radius + 150)

              return (
                <AnimatePresence key={`sublines-${genre.id}`}>
                  {genre.children.map((child, childIndex) => {
                    const { x: childX, y: childY } = subPositions[childIndex]

                    return (
                      <motion.line
                        key={`subline-${child.id}`}
                        x1={mainX}
                        y1={mainY}
                        x2={childX}
                        y2={childY}
                        stroke="#D4A574"
                        strokeWidth={2}
                        strokeDasharray="3 3"
                        initial={{ pathLength: 0, opacity: 0 }}
                        animate={{ pathLength: 1, opacity: 1 }}
                        exit={{ pathLength: 0, opacity: 0 }}
                        transition={{ duration: 0.3, delay: childIndex * 0.05 }}
                      />
                    )
                  })}
                </AnimatePresence>
              )
            })}

            {/* Sub-sub-genre lines */}
            {genres.map((genre, index) => {
              const mainAngle = (index / genres.length) * 2 * Math.PI - Math.PI / 2
              const isExpanded = expandedGenre === genre.id

              if (!isExpanded || !genre.children) return null

              const subPositions = calculatePositions(genre.children.length, mainAngle, 1.2, radius + 150)

              return (
                <AnimatePresence key={`subsublines-${genre.id}`}>
                  {genre.children.map((child, childIndex) => {
                    const isSubExpanded = expandedSubGenre === child.id
                    const { x: childX, y: childY, angle: childAngle } = subPositions[childIndex]

                    if (!isSubExpanded || !child.children) return null

                    const subSubPositions = calculatePositions(child.children.length, childAngle, 0.8, radius + 300)

                    return child.children.map((grandchild, grandchildIndex) => {
                      const { x: grandchildX, y: grandchildY } = subSubPositions[grandchildIndex]

                      return (
                        <motion.line
                          key={`subsubline-${grandchild.id}`}
                          x1={childX}
                          y1={childY}
                          x2={grandchildX}
                          y2={grandchildY}
                          stroke="#C17D47"
                          strokeWidth={2}
                          strokeDasharray="2 2"
                          initial={{ pathLength: 0, opacity: 0 }}
                          animate={{ pathLength: 1, opacity: 1 }}
                          exit={{ pathLength: 0, opacity: 0 }}
                          transition={{ duration: 0.3, delay: grandchildIndex * 0.05 }}
                        />
                      )
                    })
                  })}
                </AnimatePresence>
              )
            })}
          </g>

          <g className="circles-layer">
            <motion.circle
              cx={centerX}
              cy={centerY}
              r={70}
              fill="#D4A574"
              stroke="#6B5B55"
              strokeWidth={3}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, type: "spring" }}
            />
            <text
              x={centerX}
              y={centerY}
              textAnchor="middle"
              dominantBaseline="middle"
              className="fill-[#3E2723] font-['Zilla_Slab',serif] text-base font-semibold pointer-events-none"
            >
              Select
            </text>
            <text
              x={centerX}
              y={centerY + 20}
              textAnchor="middle"
              dominantBaseline="middle"
              className="fill-[#3E2723] font-['Zilla_Slab',serif] text-base font-semibold pointer-events-none"
            >
              Genre
            </text>

            {/* Main genre circles */}
            {genres.map((genre, index) => {
              const angle = (index / genres.length) * 2 * Math.PI - Math.PI / 2
              const x = centerX + radius * Math.cos(angle)
              const y = centerY + radius * Math.sin(angle)
              const isExpanded = expandedGenre === genre.id
              const isHovered = hoveredGenre === genre.id

              return (
                <g key={genre.id}>
                  <motion.g
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                    style={{ cursor: "pointer" }}
                    onMouseEnter={() => setHoveredGenre(genre.id)}
                    onMouseLeave={() => setHoveredGenre(null)}
                    onClick={() => handleGenreClick(genre)}
                  >
                    <circle
                      cx={x}
                      cy={y}
                      r={isExpanded ? 65 : isHovered ? 58 : 55}
                      fill={isExpanded ? "#557153" : "#6B8E6A"}
                      stroke={isExpanded ? "#3E2723" : "#557153"}
                      strokeWidth={isExpanded ? 3 : 2}
                      className="transition-all duration-300"
                    />

                    <text
                      x={x}
                      y={y - 5}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      className="fill-white font-['Zilla_Slab',serif] text-sm font-semibold pointer-events-none"
                    >
                      {genre.name}
                    </text>

                    {genre.percentage && (
                      <text
                        x={x}
                        y={y + 12}
                        textAnchor="middle"
                        dominantBaseline="middle"
                        className="fill-white/80 text-xs pointer-events-none"
                      >
                        {genre.percentage}%
                      </text>
                    )}
                  </motion.g>

                  {/* Sub-genre circles */}
                  <AnimatePresence>
                    {isExpanded && genre.children && (
                      <>
                        {genre.children.map((child, childIndex) => {
                          const subPositions = calculatePositions(genre.children!.length, angle, 1.2, radius + 150)
                          const { x: childX, y: childY } = subPositions[childIndex]
                          const isSubExpanded = expandedSubGenre === child.id

                          return (
                            <g key={child.id}>
                              <motion.g
                                initial={{ scale: 0, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                exit={{ scale: 0, opacity: 0 }}
                                transition={{ duration: 0.3, delay: childIndex * 0.05 }}
                                style={{ cursor: "pointer" }}
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handleSubGenreClick(genre, child)
                                }}
                              >
                                <circle
                                  cx={childX}
                                  cy={childY}
                                  r={isSubExpanded ? 45 : 42}
                                  fill={isSubExpanded ? "#C17D47" : "#D4A574"}
                                  stroke="#8D6E63"
                                  strokeWidth={isSubExpanded ? 3 : 2}
                                  className="hover:fill-[#C17D47] transition-all duration-200"
                                />

                                <text
                                  x={childX}
                                  y={childY}
                                  textAnchor="middle"
                                  dominantBaseline="middle"
                                  className="fill-white font-['Zilla_Slab',serif] text-sm font-medium pointer-events-none"
                                >
                                  {child.name.length > 15 ? `${child.name.substring(0, 13)}...` : child.name}
                                </text>

                                {child.children && child.children.length > 0 && (
                                  <circle
                                    cx={childX + 24}
                                    cy={childY - 24}
                                    r={7}
                                    fill="#3E2723"
                                    className="pointer-events-none"
                                  />
                                )}
                              </motion.g>

                              {/* Sub-sub-genre circles (3rd level) */}
                              <AnimatePresence>
                                {isSubExpanded && child.children && (
                                  <>
                                    {child.children.map((grandchild, grandchildIndex) => {
                                      const subSubPositions = calculatePositions(
                                        child.children!.length,
                                        subPositions[childIndex].angle,
                                        0.8,
                                        radius + 300,
                                      )
                                      const { x: grandchildX, y: grandchildY } = subSubPositions[grandchildIndex]

                                      return (
                                        <motion.g
                                          key={grandchild.id}
                                          initial={{ scale: 0, opacity: 0 }}
                                          animate={{ scale: 1, opacity: 1 }}
                                          exit={{ scale: 0, opacity: 0 }}
                                          transition={{ duration: 0.3, delay: grandchildIndex * 0.05 }}
                                          style={{ cursor: "pointer" }}
                                          onClick={(e) => {
                                            e.stopPropagation()
                                            handleSubSubGenreClick(genre, child, grandchild)
                                          }}
                                        >
                                          <circle
                                            cx={grandchildX}
                                            cy={grandchildY}
                                            r={35}
                                            fill="#E76F51"
                                            stroke="#6B5B55"
                                            strokeWidth={2}
                                            className="hover:fill-[#F28B6F] transition-colors duration-200"
                                          />

                                          <text
                                            x={grandchildX}
                                            y={grandchildY}
                                            textAnchor="middle"
                                            dominantBaseline="middle"
                                            className="fill-white font-['Zilla_Slab',serif] text-xs font-medium pointer-events-none"
                                          >
                                            {grandchild.name.length > 12
                                              ? `${grandchild.name.substring(0, 10)}...`
                                              : grandchild.name}
                                          </text>
                                        </motion.g>
                                      )
                                    })}
                                  </>
                                )}
                              </AnimatePresence>
                            </g>
                          )
                        })}
                      </>
                    )}
                  </AnimatePresence>
                </g>
              )
            })}
          </g>
        </svg>
      </motion.div>

      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 text-center">
        <p className="text-base text-[#6B5B55] font-['Zilla_Slab',serif]">
          {expandedSubGenre
            ? "Click a specific topic or the sub-genre again"
            : expandedGenre
              ? "Click a sub-genre to expand or select"
              : "Click a genre to expand or select"}
        </p>
      </div>
    </div>
  )
}
