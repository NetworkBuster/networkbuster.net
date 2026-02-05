import './LieDetector.css'
import { useState } from 'react'

function LieDetector() {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState([])
  const [lieDetected, setLieDetected] = useState(false)
  const [gameStarted, setGameStarted] = useState(false)
  const [isInJail, setIsInJail] = useState(false)

  const questions = [
    {
      id: 1,
      question: "Did you access the secure server without authorization?",
      truthAnswer: "yes"
    },
    {
      id: 2,
      question: "Have you shared your credentials with anyone?",
      truthAnswer: "no"
    },
    {
      id: 3,
      question: "Did you follow all security protocols today?",
      truthAnswer: "yes"
    },
    {
      id: 4,
      question: "Have you ever bypassed the firewall?",
      truthAnswer: "no"
    },
    {
      id: 5,
      question: "Do you understand the consequences of security breaches?",
      truthAnswer: "yes"
    }
  ]

  const startGame = () => {
    setGameStarted(true)
    setCurrentQuestion(0)
    setAnswers([])
    setLieDetected(false)
    setIsInJail(false)
  }

  const handleAnswer = (answer) => {
    const currentQ = questions[currentQuestion]
    const isLying = answer !== currentQ.truthAnswer
    
    const newAnswer = {
      question: currentQ.question,
      answer: answer,
      isLie: isLying
    }
    
    setAnswers([...answers, newAnswer])

    if (isLying) {
      setLieDetected(true)
      setTimeout(() => {
        setIsInJail(true)
      }, 1500)
    } else if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
    } else {
      // All questions answered truthfully
      setTimeout(() => {
        alert('All questions answered truthfully! You are free to go.')
        startGame()
      }, 1000)
    }
  }

  if (isInJail) {
    return (
      <div className="lie-detector-page jail-screen">
        <div className="jail-container">
          <div className="jail-bars">
            <div className="bar"></div>
            <div className="bar"></div>
            <div className="bar"></div>
            <div className="bar"></div>
            <div className="bar"></div>
            <div className="bar"></div>
          </div>
          <div className="jail-content">
            <h1>🚨 LIE DETECTED! 🚨</h1>
            <h2>CONSEQUENCE: JAIL</h2>
            <div className="mugshot">
              <div className="prisoner">👮‍♀️➡️🔒</div>
              <div className="prisoner-id">Donna Middleton</div>
              <div className="charge">Charge: Providing False Information</div>
            </div>
            <div className="sentence">
              <p>You have been caught lying during the security interrogation.</p>
              <p>Sentence: Immediate detention in the NetworkBuster Security Facility.</p>
            </div>
            <button className="btn-restart" onClick={startGame}>
              Retry Interrogation
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!gameStarted) {
    return (
      <div className="lie-detector-page">
        <div className="lie-detector-intro">
          <h1>🔍 Donna Middleton's Lie Detector</h1>
          <div className="officer-badge">
            <div className="badge-icon">👮‍♀️</div>
            <div className="badge-info">
              <h2>Security Specialist</h2>
              <h3>Donna Middleton</h3>
              <p>Truth Verification Division</p>
            </div>
          </div>
          <div className="intro-content">
            <p className="warning">⚠️ WARNING: All statements will be analyzed for truthfulness.</p>
            <div className="rules">
              <h3>Interrogation Rules:</h3>
              <ul>
                <li>Answer all questions honestly</li>
                <li>Any detected lie will result in immediate consequences</li>
                <li>Consequence for lying: <strong className="jail-warning">JAIL</strong></li>
                <li>Complete all questions truthfully to pass</li>
              </ul>
            </div>
            <button className="btn-start" onClick={startGame}>
              Begin Lie Detector Test
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="lie-detector-page">
      <div className="lie-detector-header">
        <h1>🔍 Lie Detector Interrogation</h1>
        <div className="interrogation-info">
          <span className="officer">Officer: Donna Middleton 👮‍♀️</span>
          <span className="progress">Question {currentQuestion + 1} of {questions.length}</span>
        </div>
      </div>

      {lieDetected ? (
        <div className="lie-detected-animation">
          <div className="alert-box">
            <h2>⚠️ LIE DETECTED ⚠️</h2>
            <p>Processing consequence...</p>
            <div className="loading-bar">
              <div className="loading-progress"></div>
            </div>
          </div>
        </div>
      ) : (
        <div className="interrogation-room">
          <div className="question-display">
            <div className="question-number">Question #{currentQuestion + 1}</div>
            <h2 className="question-text">{questions[currentQuestion].question}</h2>
          </div>

          <div className="answer-buttons">
            <button 
              className="btn-answer btn-yes"
              onClick={() => handleAnswer('yes')}
            >
              ✓ YES
            </button>
            <button 
              className="btn-answer btn-no"
              onClick={() => handleAnswer('no')}
            >
              ✗ NO
            </button>
          </div>

          <div className="polygraph-display">
            <div className="polygraph-label">Polygraph Reading:</div>
            <div className="polygraph-line">
              <div className="wave"></div>
            </div>
          </div>

          {answers.length > 0 && (
            <div className="answer-history">
              <h3>Previous Responses:</h3>
              <ul>
                {answers.map((ans, idx) => (
                  <li key={idx} className={ans.isLie ? 'lie-answer' : 'truth-answer'}>
                    Q{idx + 1}: {ans.answer.toUpperCase()} {ans.isLie ? '❌' : '✓'}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default LieDetector
