import React, { useContext, useEffect, useState } from 'react'
import { AppContext } from '../context/AppContext'
import { useNavigate, useParams } from 'react-router-dom'
import { assets } from '../assets/assets'

const Doctors = () => {

  const { speciality } = useParams()

  const [filterDoc, setFilterDoc] = useState([])
  const [showFilter, setShowFilter] = useState(false)
  const navigate = useNavigate();

  const { doctors, token } = useContext(AppContext)

  const applyFilter = () => {
    if (speciality) {
      setFilterDoc(doctors.filter(doc => doc.clinic_type_slug === speciality))
    } else {
      setFilterDoc(doctors)
    }
  }

  useEffect(() => {
    applyFilter()
  }, [doctors, speciality])

  return (
    <div>
      <p className='text-gray-600'>Browse through the clinic types.</p>
      <div className='flex flex-col sm:flex-row items-start gap-5 mt-5'>
        <button onClick={() => setShowFilter(!showFilter)} className={`py-1 px-3 border rounded text-sm  transition-all sm:hidden ${showFilter ? 'bg-primary text-white' : ''}`}>Filters</button>
        <div className={`flex-col gap-4 text-sm text-gray-600 ${showFilter ? 'flex' : 'hidden sm:flex'}`}>
          <p onClick={() => speciality === 'general-outpatient-clinic' ? navigate('/doctors') : navigate('/doctors/general-outpatient-clinic')} className={`w-[94vw] sm:w-auto pl-3 py-1.5 pr-16 border border-gray-300 rounded transition-all cursor-pointer ${speciality === 'general-outpatient-clinic' ? 'bg-[#E2E5FF] text-black ' : ''}`}>General Outpatient Clinic</p>
          <p onClick={() => speciality === 'surgery-clinic' ? navigate('/doctors') : navigate('/doctors/surgery-clinic')} className={`w-[94vw] sm:w-auto pl-3 py-1.5 pr-16 border border-gray-300 rounded transition-all cursor-pointer ${speciality === 'surgery-clinic' ? 'bg-[#E2E5FF] text-black ' : ''}`}>Surgery Clinic</p>
          <p onClick={() => speciality === 'physician-clinic' ? navigate('/doctors') : navigate('/doctors/physician-clinic')} className={`w-[94vw] sm:w-auto pl-3 py-1.5 pr-16 border border-gray-300 rounded transition-all cursor-pointer ${speciality === 'physician-clinic' ? 'bg-[#E2E5FF] text-black ' : ''}`}>Physician Clinic</p>
          <p onClick={() => speciality === 'immunization-clinic' ? navigate('/doctors') : navigate('/doctors/immunization-clinic')} className={`w-[94vw] sm:w-auto pl-3 py-1.5 pr-16 border border-gray-300 rounded transition-all cursor-pointer ${speciality === 'immunization-clinic' ? 'bg-[#E2E5FF] text-black ' : ''}`}>Immunization Clinic</p>
          <p onClick={() => speciality === 'antenatal-clinic' ? navigate('/doctors') : navigate('/doctors/antenatal-clinic')} className={`w-[94vw] sm:w-auto pl-3 py-1.5 pr-16 border border-gray-300 rounded transition-all cursor-pointer ${speciality === 'antenatal-clinic' ? 'bg-[#E2E5FF] text-black ' : ''}`}>Antenatal Clinic</p>
          <p onClick={() => speciality === 'wellness-clinic' ? navigate('/doctors') : navigate('/doctors/wellness-clinic')} className={`w-[94vw] sm:w-auto pl-3 py-1.5 pr-16 border border-gray-300 rounded transition-all cursor-pointer ${speciality === 'wellness-clinic' ? 'bg-[#E2E5FF] text-black ' : ''}`}>Wellness Clinic</p>
        </div>
        <div className="w-full">
          {/* Case 1: No token */}
          {!token ? (
            <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded-lg text-center">
              Please login to see doctors
            </div>
          ) : filterDoc.length === 0 ? (
            // Case 2: Logged in but no doctors
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg text-center">
              No doctor for this clinic
            </div>
          ) : (
            // Case 3: Show doctors
            <div className="grid grid-cols-auto gap-4 gap-y-6">
              {filterDoc.map((item, index) => (
                <div
                  key={index}
                  onClick={() => {
                    navigate(`/appointment/${item.clinic_type_slug}/${item.id}`);
                    scrollTo(0, 0);
                  }}
                  className="border border-[#C9D8FF] rounded-xl overflow-hidden cursor-pointer hover:translate-y-[-10px] transition-all duration-500"
                >
                  <img className="bg-[#EAEFFF]" src={assets.doc1} alt="" />
                  <div className="p-4">
                    <div
                      className={`flex items-center gap-2 text-sm text-center ${
                        item.is_available ? "text-green-500" : "text-gray-500"
                      }`}
                    >
                      <p
                        className={`w-2 h-2 rounded-full ${
                          item.is_available ? "bg-green-500" : "bg-gray-500"
                        }`}
                      ></p>
                      <p>{item.is_available ? "Available" : "Not Available"}</p>
                    </div>
                    <p className="text-[#262626] text-lg font-medium">{item.name}</p>
                    <p className="text-[#5C5C5C] text-sm">{item.speciality}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Doctors