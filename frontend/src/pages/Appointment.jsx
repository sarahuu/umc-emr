import React, { useContext, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { AppContext } from '../context/AppContext'
import { assets } from '../assets/assets'
import axios from 'axios'
import { toast } from 'react-toastify'

const Appointment = () => {

    const { specialty, docId } = useParams()
    const { doctors, backendUrl, token, getDoctosData, userData } = useContext(AppContext)
    const [note, setNote] = useState("");

    const [docInfo, setDocInfo] = useState(false)
    const [docSlots, setDocSlots] = useState([])
    const [slotIndex, setSlotIndex] = useState(0)
    const [slotTime, setSlotTime] = useState(null)

    const navigate = useNavigate()

    const fetchDocInfo = async () => {
    try {
        const res = await axios.get(`${backendUrl}/api/doctor/${specialty}/${docId}/availability`, {
            headers: { Authorization: `Bearer ${token}` }
        })
        setDocInfo(res.data)
        setDocSlots(res.data.availability)
    } catch (err) {
        console.error("Error fetching doctor info", err)
    }
}

    const bookAppointment = async () => {
        if (!token) {
            toast.warning("Login to book appointment");
            return navigate("/login");
        }
        const selectedDay = docSlots[slotIndex];
        if (!selectedDay) {
            toast.error("Please select a date");
            return;
        }
        if (!slotTime || !slotTime.id) {
            toast.error("Please select a time slot");
            return;
        }
        if (!note) {
            toast.error("Please describe your need for consultation");
            return;
        }

        try {
            const { data } = await axios.post(
            backendUrl + "/api/user/book-appointment",
            {
                slotId: slotTime.id,
                patientId: userData.uid,
                note: note
            },
            { headers: { Authorization: `Bearer ${token}` } }
            );

            if (data.success) {
                toast.success(data.message);
                getDoctosData();
                navigate("/my-appointments");
                } else {
                toast.error(data.message);
            }
        } catch (error) {
            console.error(error);
            toast.error(error.message);
        }
    };
    useEffect(() => {
        if (doctors.length > 0) {
            fetchDocInfo()
        }
    }, [doctors, docId])

    console.log(docInfo)
    return docInfo ? (
        <div>

            {/* ---------- Doctor Details ----------- */}
            <div className='flex flex-col sm:flex-row gap-4'>
                <div>
                    <img className='bg-primary w-full sm:max-w-72 rounded-lg' src={assets.doc1} alt="" />
                </div>

                <div className='flex-1 border border-[#ADADAD] rounded-lg p-8 py-7 bg-white mx-2 sm:mx-0 mt-[-80px] sm:mt-0'>

                    {/* ----- Doc Info : name, degree, experience ----- */}

                    <p className='flex items-center gap-2 text-3xl font-medium text-gray-700'>Dr. {docInfo.name} <img className='w-5' src={assets.verified_icon} alt="" /></p>
                    <div className='flex items-center gap-2 mt-1 text-gray-600'>
                        <p>{docInfo.speciality}</p>
                    </div>

                    {/* ----- Doc About ----- */}
                    <div>
                        <p className='flex items-center gap-1 text-sm font-medium text-[#262626] mt-3'>About <img className='w-3' src={assets.info_icon} alt="" /></p>
                        <p className='text-sm text-gray-600 max-w-[700px] mt-1'>{docInfo.about}</p>
                    </div>
                </div>
            </div>

            {/* Booking slots */}
            <div className="sm:ml-72 sm:pl-4 mt-8 font-medium text-[#565656]">
                <p>Booking slots</p>
                {/* Date selector */}
                <div className="flex gap-3 items-center w-full overflow-x-scroll mt-4">
                {docSlots.map((day, index) => {
                    const dateObj = new Date(day.date);
                    return (
                    <div
                        key={index}
                        onClick={() => setSlotIndex(index)}
                        className={`text-center py-6 min-w-16 rounded-full cursor-pointer ${
                        slotIndex === index
                            ? "bg-primary text-white"
                            : "border border-[#DDDDDD]"
                        }`}
                    >
                        <p>{dateObj.toLocaleDateString("en-US", { weekday: "short" }).toUpperCase()}</p>
                        <p>{dateObj.getDate()}</p>
                    </div>
                    );
                })}
                </div>

                {/* Time selector */}
                <div className="flex items-center gap-3 w-full overflow-x-scroll mt-4">
                {docSlots.length > 0 &&
                    docSlots[slotIndex]?.slots.map((slot) => (
                    <p
                        key={slot.id}
                        onClick={() => setSlotTime(slot)}
                        className={`text-sm font-light flex-shrink-0 px-5 py-2 rounded-full cursor-pointer ${
                        slot.id === slotTime?.id
                            ? "bg-primary text-white"
                            : "text-[#949494] border border-[#B4B4B4]"
                        }`}
                    >
                        {(slot.time || "").toLowerCase()}
                    </p>
                    ))}
                </div>
                <div className="mt-6 w-full">
                    <p className="mb-2 text-sm text-gray-600">Add a note</p>
                    <textarea
                    className="w-full border border-[#DADADA] rounded-lg p-3 text-sm resize-none focus:outline-primary"
                    rows="3"
                    placeholder="E.g. Feeling feverish since yesterday..."
                    required
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                    />
                </div>

                <button
                onClick={bookAppointment}
                className="bg-primary text-white text-sm font-light px-20 py-3 rounded-full my-6"
                >
                Book an appointment
                </button>
            </div>
        </div>
    ) : null
}

export default Appointment