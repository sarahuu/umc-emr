import React from 'react'
import { assets } from '../assets/assets'

const About = () => {
  return (
    <div>

      <div className='text-center text-2xl pt-10 text-[#707070]'>
        <p>ABOUT <span className='text-gray-700 font-semibold'>US</span></p>
      </div>

      <div className='my-10 flex flex-col md:flex-row gap-12'>
        <img className='w-full md:max-w-[360px]' src={assets.about_image} alt="" />
        <div className='flex flex-col justify-center gap-6 md:w-2/4 text-sm text-gray-600'>
          <p>
            Welcome to <b>UMCEMR</b>, the University of Lagos Medical Center’s electronic medical records and patient portal. 
            UMCEMR is designed to simplify your healthcare experience, giving you convenient access to doctor appointments, medical records, and essential health services.
          </p>

          <p>
            At UMCEMR, we recognize the challenges patients face when managing their health and keeping track of appointments. 
            This portal serves as a bridge between you and the Medical Center, ensuring that scheduling, records management, and ongoing care are all accessible in one place.
          </p>

          <b className='text-gray-800'>Our Vision</b>
          <p>
            Our vision at UMCEMR is to create a seamless and reliable healthcare experience for every student, staff, and member of the University community. 
            We aim to connect patients with healthcare providers through technology, making it easier to access the right care at the right time, while reducing paperwork and improving efficiency.
          </p>
        </div>
      </div>
    </div>
  )
}

export default About
