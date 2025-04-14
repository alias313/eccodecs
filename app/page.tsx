"use client";

import React, { useState, useCallback } from "react";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

const asciiToBinary = (asciiString: string): string => {
  if (!asciiString) return "";
  return asciiString
    .split("")
    .map((char) => char.charCodeAt(0).toString(2).padStart(8, "0"))
    .join(" ");
};

const binaryToAscii = (binaryString: string): string => {
  if (!binaryString) return "";
  const cleanedString = binaryString.trim().replace(/\s+/g, " ");
  const binaryChunks = cleanedString.split(" ");
  try {
    return binaryChunks
      .map((chunk) => {
        if (!/^[01]{1,8}$/.test(chunk) && chunk !== "") {
          console.warn(`Skipping invalid binary chunk: ${chunk}`);
          throw new Error(`Invalid binary chunk: ${chunk}`);
        }
        if (chunk === "") return ""; // Skip empty chunks resulting from multiple spaces
        return String.fromCharCode(parseInt(chunk, 2));
      })
      .join("");
  } catch (error) {
    console.error("Error converting binary to ASCII:", error);
    return "Error: Invalid binary input";
  }
};

export default function Home() {
  const [currentTab, setCurrentTab] = useState<"ascii" | "binary">("ascii");
  const [textValue, setTextValue] = useState<string>("");

  const handleTabSwitch = useCallback(
    (newTabValue: string) => {
      const newTab = newTabValue as "ascii" | "binary";

      if (newTab === currentTab) return;

      let convertedValue = "";
      if (newTab === "binary") {
        convertedValue = asciiToBinary(textValue);
      } else {
        convertedValue = binaryToAscii(textValue);
      }

      setCurrentTab(newTab);
      setTextValue(convertedValue);
    },
    [textValue, currentTab]
  );

  const handleTextChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setTextValue(event.target.value);
  };

  const getPlaceholderText = () => {
    return currentTab === "ascii"
      ? "Enter ASCII text here..."
      : "Enter Binary text here (e.g., 01101000 01101001)";
  };

  return (
    <main className="container mx-auto p-4 md:p-8">
      <h1 className="mb-6 text-2xl font-semibold tracking-tight items-center justify-center text-center">
        Reed-Solomon Encoder
      </h1>

      <Tabs 
        value={currentTab}
        onValueChange={handleTabSwitch}
        defaultValue="ascii"
        className="w-full items-center justify-center"
      >
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="ascii">ASCII</TabsTrigger>
          <TabsTrigger value="binary">Binary</TabsTrigger>
        </TabsList>
      </Tabs>

      <div className="mt-4 w-full items-center justify-center">
        <Label htmlFor="converter-textarea" className="sr-only">
          Input/Output
        </Label>
        <Textarea
          id="converter-textarea"
          value={textValue}
          onChange={handleTextChange}
          placeholder={getPlaceholderText()}
          rows={10}
          className={`mt-1 text-base ${
            currentTab === "binary" ? "font-mono" : ""
          }`}
        />
      </div>
    </main>
  );
}
